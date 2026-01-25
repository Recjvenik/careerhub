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

def generate_otp():
    return str(random.randint(100000, 999999))

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Don't save yet, store in session
            user_data = {
                'full_name': form.cleaned_data['full_name'],
                'mobile': form.cleaned_data['mobile'],
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password']
            }
            
            # Generate OTP
            mobile = user_data['mobile']
            otp_code = generate_otp()
            OTP.objects.create(mobile=mobile, otp=otp_code)
            print(f"OTP for {mobile}: {otp_code}") # For dev
            
            # Store in session
            request.session['registration_data'] = user_data
            request.session['verify_mobile'] = mobile
            
            return redirect('verify_registration_otp')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def verify_registration_otp(request):
    mobile = request.session.get('verify_mobile')
    user_data = request.session.get('registration_data')
    
    if not mobile or not user_data:
        return redirect('register')
        
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        
        try:
            otp_record = OTP.objects.filter(mobile=mobile, otp=otp_input, is_verified=False).latest('created_at')
            
            # Check expiration (5 minutes)
            if otp_record.created_at < timezone.now() - timedelta(minutes=5):
                messages.error(request, "OTP has expired. Please request a new one.")
                return redirect('verify_registration_otp')

            otp_record.is_verified = True
            otp_record.save()
            
            # Create user
            user = CustomUser.objects.create_user(
                mobile=user_data['mobile'],
                email=user_data['email'],
                password=user_data['password'],
                full_name=user_data['full_name']
            )
            user.is_verified = True
            user.save()
            
            # Login user
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Clear session
            del request.session['verify_mobile']
            del request.session['registration_data']
            
            messages.success(request, "Confirm Your OTP to Get Started!")
            return redirect('index')
            
        except OTP.DoesNotExist:
            messages.error(request, "Invalid OTP")
            
    return render(request, 'users/verify_otp.html', {'action_url': 'verify_registration_otp'})

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
            # Logic to find user and send OTP
            # For now, we'll just assume mobile for OTP generation as per previous logic
            # In a real app, we'd check if it's email or mobile and send accordingly
            
            if '@' in mobile_or_email:
                user = CustomUser.objects.get(email=mobile_or_email)
                mobile = user.mobile
            else:
                mobile = mobile_or_email
                
            otp_code = generate_otp()
            OTP.objects.create(mobile=mobile, otp=otp_code)
            print(f"OTP for {mobile}: {otp_code}") # For dev
            request.session['reset_mobile'] = mobile
            return redirect('reset_password')
    else:
        form = ForgotPasswordForm()
    return render(request, 'users/forgot_password.html', {'form': form})

def reset_password_view(request):
    mobile = request.session.get('reset_mobile')
    if not mobile:
        return redirect('forgot_password')
        
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            otp_input = form.cleaned_data['otp']
            new_password = form.cleaned_data['new_password']
            
            try:
                otp_record = OTP.objects.filter(mobile=mobile, otp=otp_input, is_verified=False).latest('created_at')
                otp_record.is_verified = True
                otp_record.save()
                
                user = CustomUser.objects.get(mobile=mobile)
                user.set_password(new_password)
                user.save()
                
                messages.success(request, "Password reset successfully. Please login.")
                del request.session['reset_mobile']
                return redirect('login')
            except OTP.DoesNotExist:
                form.add_error('otp', "Invalid OTP")
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

