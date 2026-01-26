import random
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import CustomUser, OTP
from .forms import UserRegistrationForm, UserLoginForm, ForgotPasswordForm, ResetPasswordForm, ProfileUpdateForm
from django.db.models import Q
from .utils import fetch_phone_email_data

def generate_otp():
    return str(random.randint(100000, 999999))

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Store data in session for post-verification creation
            user_data = {
                'full_name': form.cleaned_data['full_name'],
                'mobile': form.cleaned_data['mobile'],
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password']
            }
            request.session['registration_data'] = user_data
            request.session['verification_type'] = 'registration'
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'redirect_url': '/auth/verify-registration-otp/'})
            return redirect('verify_registration_otp')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': form.errors.as_text()
                }, status=400)
    else:
        form = UserRegistrationForm()
    
    response = render(request, 'users/register.html', {'form': form})
    response['Cross-Origin-Opener-Policy'] = 'same-origin-allow-popups'
    return response

def verify_registration_otp(request):
    # This view will now just render the page with the Phone Email button
    verification_type = request.session.get('verification_type')
    if not verification_type:
        return redirect('register')
        
    response = render(request, 'users/verify_otp.html', {
        'verification_type': verification_type,
        'reset_identifier': request.session.get('reset_identifier'),
        'client_id': "13443371295433469166" # Provided in the snippet
    })
    response['Cross-Origin-Opener-Policy'] = 'same-origin-allow-popups'
    return response

def phone_email_callback(request):
    """Handle the user_json_url from Phone Email"""
    user_json_url = request.GET.get('user_json_url')
    if not user_json_url:
        return JsonResponse({'status': 'error', 'message': 'No URL provided'}, status=400)

    data = fetch_phone_email_data(user_json_url)
    if not data:
        return JsonResponse({'status': 'error', 'message': 'Failed to fetch user data'}, status=500)

    verification_type = request.session.get('verification_type')
    
    if verification_type == 'registration':
        user_data = request.session.get('registration_data')
        if not user_data:
            return JsonResponse({'status': 'error', 'message': 'Registration session expired'}, status=400)
            
        # Strict Verification: Ensure the verified phone matches the input phone
        verified_phone = data.get("user_phone_number")
        input_phone = user_data.get('mobile')
        
        # Simple normalization: keep only last 10 digits for comparison
        norm_verified = ''.join(filter(str.isdigit, verified_phone))[-10:] if verified_phone else ""
        norm_input = ''.join(filter(str.isdigit, input_phone))[-10:] if input_phone else ""
        
        if norm_verified != norm_input:
            return JsonResponse({
                'status': 'error', 
                'message': f'Verification failed: Verified number ({verified_phone}) does not match registered number ({input_phone}).'
            }, status=400)
        
        # Create user
        try:
            user = CustomUser.objects.create_user(
                mobile=user_data['mobile'],
                email=user_data['email'],
                password=user_data['password'],
                full_name=user_data['full_name']
            )
            user.is_verified = True
            user.save()
            
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Clear session
            del request.session['registration_data']
            del request.session['verification_type']
            
            return JsonResponse({'status': 'success', 'redirect_url': '/'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    elif verification_type == 'forgot_password':
        reset_identifier = request.session.get('reset_identifier')
        if not reset_identifier:
            return JsonResponse({'status': 'error', 'message': 'Reset session expired'}, status=400)
            
        verified_email = data.get("user_email_id")
        verified_phone = data.get("user_phone_number")
        
        try:
            if '@' in reset_identifier:
                # Email verification case
                if reset_identifier.lower() != (verified_email or "").lower():
                    return JsonResponse({
                        'status': 'error', 
                        'message': f'Verification failed: Verified email ({verified_email}) does not match requested email ({reset_identifier}).'
                    }, status=400)
                user = CustomUser.objects.get(email=reset_identifier)
            else:
                # Mobile verification case
                norm_verified = ''.join(filter(str.isdigit, verified_phone))[-10:] if verified_phone else ""
                norm_input = ''.join(filter(str.isdigit, reset_identifier))[-10:] if reset_identifier else ""
                
                if norm_verified != norm_input:
                    return JsonResponse({
                        'status': 'error', 
                        'message': f'Verification failed: Verified number ({verified_phone}) does not match requested number ({reset_identifier}).'
                    }, status=400)
                user = CustomUser.objects.get(mobile=reset_identifier)
            
            request.session['reset_user_id'] = user.id
            request.session['is_verified'] = True
            return JsonResponse({'status': 'success', 'redirect_url': '/auth/reset-password/'})
        except CustomUser.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found in our records.'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid verification type'}, status=400)

def resend_otp_view(request):
    mobile = request.session.get('verify_mobile')
    if not mobile:
        messages.error(request, "Session expired. Please start over.")
        return redirect('register')
        
    # Generate new OTP
    otp_code = generate_otp()
    OTP.objects.create(mobile=mobile, otp=otp_code)
    print(f"Resent OTP for {mobile}: {otp_code}") # For dev
    
    messages.success(request, "A new OTP has been sent to your mobile number.")
    
    # Determine where to redirect based on referer or session
    # For now, default to verify_registration_otp if registration_data exists
    if request.session.get('registration_data'):
        return redirect('verify_registration_otp')
        
    return redirect('login') # Fallback

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            return redirect('index')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})

def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            mobile_or_email = form.cleaned_data['mobile_or_email']
            request.session['reset_identifier'] = mobile_or_email
            request.session['verification_type'] = 'forgot_password'
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'verification_type': 'email' if '@' in mobile_or_email else 'mobile'
                })
            return redirect('verify_registration_otp')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': form.errors.as_text()
                }, status=400)
    else:
        form = ForgotPasswordForm()
    
    response = render(request, 'users/forgot_password.html', {'form': form})
    response['Cross-Origin-Opener-Policy'] = 'same-origin-allow-popups'
    return response

def reset_password_view(request):
    user_id = request.session.get('reset_user_id')
    is_verified = request.session.get('is_verified')
    
    if not user_id or not is_verified:
        return redirect('forgot_password')
        
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        # Note: We need to update ResetPasswordForm to not require OTP field since we verified it via third party
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            
            try:
                user = CustomUser.objects.get(id=user_id)
                user.set_password(new_password)
                user.save()
                
                messages.success(request, "Password reset successfully. Please login.")
                del request.session['reset_user_id']
                del request.session['is_verified']
                del request.session['reset_identifier']
                return redirect('login')
            except CustomUser.DoesNotExist:
                messages.error(request, "User not found")
    else:
        form = ResetPasswordForm()
        
    return render(request, 'users/reset_password.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

from assessments.models import Assessment
from courses.models import Enrollment

@login_required
def dashboard_view(request):
    user = request.user
    # Get completed assessment
    assessment = Assessment.objects.filter(user=user, status='completed').last()
    
    # Get active enrollment
    active_enrollment = Enrollment.objects.filter(user=user, status='active').first()
    
    # Get recommended courses if assessment done but no active enrollment
    recommended_courses = []
    if assessment and not active_enrollment:
        # Assuming result_data has recommended_courses list
        recommended_courses = assessment.result_data.get('recommended_courses', [])
        
    return render(request, 'users/dashboard.html', {
        'user': user,
        'assessment': assessment,
        'active_enrollment': active_enrollment,
        'recommended_courses': recommended_courses
    })

@login_required
def profile_view(request):
    # Prefetch related objects to avoid N+1 queries in template
    user = CustomUser.objects.select_related('college', 'branch', 'degree', 'city', 'state').get(pk=request.user.pk)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            if user.city and user.state:
                user.location = f"{user.city.name}, {user.state.name}"
            user.save()
            messages.success(request, 'Profile updated successfully!')
            
            # Check if assessment is completed
            if Assessment.objects.filter(user=user, status='completed').exists():
                return redirect('dashboard')
            else:
                return redirect('start_assessment')
    else:
        form = ProfileUpdateForm(instance=user)

    # Calculate profile completion - use _id for ForeignKey fields to avoid extra DB queries
    fields = ['full_name', 'email', 'mobile', 'gender', 'degree_id', 'college_id', 'branch_id', 'city_id', 'state_id']
    filled_fields = 0
    for field in fields:
        if getattr(user, field):
            filled_fields += 1
    
    completion_percentage = int((filled_fields / len(fields)) * 100)

    return render(request, 'users/profile.html', {
        'form': form,
        'completion_percentage': completion_percentage,
        'user': user  # Pass prefetched user to avoid extra queries in template
    })

from django.http import JsonResponse
from core.models import Degree

def search_degrees(request):
    query = request.GET.get('q', '')
    if len(query) >= 1:
        degrees = Degree.objects.filter(Q(name__icontains=query) | Q(full_name__icontains=query))[:10]
        results = [{'id': d.id, 'name': f"{d.name} - {d.full_name}"} for d in degrees]
    else:
        # Return all degrees when no query (for dropdown)
        degrees = Degree.objects.all()[:10]
        results = [{'id': d.id, 'name': f"{d.name} - {d.full_name}"} for d in degrees]
    return JsonResponse(results, safe=False)

