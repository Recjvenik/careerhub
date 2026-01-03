import random
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser, OTP
from .forms import UserRegistrationForm, UserLoginForm, ForgotPasswordForm, ResetPasswordForm, ProfileUpdateForm

def generate_otp():
    return str(random.randint(100000, 999999))

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('index')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

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
    user = request.user
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

    # Calculate profile completion
    fields = ['full_name', 'email', 'mobile', 'gender', 'college', 'branch', 'city', 'state']
    filled_fields = 0
    for field in fields:
        if getattr(user, field):
            filled_fields += 1
    
    completion_percentage = int((filled_fields / len(fields)) * 100)

    return render(request, 'users/profile.html', {
        'form': form,
        'completion_percentage': completion_percentage
    })
