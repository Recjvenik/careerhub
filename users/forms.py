from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import CustomUser

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all',
        'placeholder': 'Create a password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all',
        'placeholder': 'Confirm password'
    }))

    class Meta:
        model = CustomUser
        fields = ['full_name', 'mobile', 'email']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all',
                'placeholder': 'Enter your full name'
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all',
                'placeholder': 'Enter mobile number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all',
                'placeholder': 'Enter email address'
            }),
        }

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if mobile:
            # Remove any non-digit characters
            mobile = ''.join(filter(str.isdigit, mobile))
            
            # Check length (assuming Indian mobile numbers)
            if len(mobile) != 10:
                raise ValidationError("Mobile number must be 10 digits.")
            
            # Check if mobile already exists
            if CustomUser.objects.filter(mobile=mobile).exists():
                raise ValidationError("This mobile number is already registered.")
                
        return mobile

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise ValidationError("Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class UserLoginForm(forms.Form):
    username = forms.CharField(label='Mobile or Email', widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all',
        'placeholder': 'Enter mobile or email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all',
        'placeholder': 'Enter password'
    }))

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            # Check if username is mobile or email
            if '@' in username:
                try:
                    user = CustomUser.objects.get(email=username)
                    username = user.mobile
                except CustomUser.DoesNotExist:
                    pass
            
            user = authenticate(username=username, password=password)
            if not user:
                raise ValidationError("Invalid credentials")
            cleaned_data['user'] = user
        return cleaned_data

class ForgotPasswordForm(forms.Form):
    mobile_or_email = forms.CharField(label='Mobile or Email', widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all',
        'placeholder': 'Enter registered mobile or email'
    }))

    def clean_mobile_or_email(self):
        data = self.cleaned_data['mobile_or_email']
        if '@' in data:
            if not CustomUser.objects.filter(email=data).exists():
                raise ValidationError("No user found with this email")
        else:
            if not CustomUser.objects.filter(mobile=data).exists():
                raise ValidationError("No user found with this mobile number")
        return data

class ResetPasswordForm(forms.Form):
    otp = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all',
        'placeholder': 'Enter 6-digit OTP'
    }))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all',
        'placeholder': 'Enter new password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all',
        'placeholder': 'Confirm new password'
    }))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise ValidationError("Passwords do not match")
        return cleaned_data

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'mobile', 'gender', 'college', 'branch', 'city', 'state']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6',
                'placeholder': 'Enter your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6',
                'placeholder': 'Enter email address'
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6',
                'placeholder': 'Enter mobile number'
            }),
            'gender': forms.Select(attrs={
                'class': 'block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6'
            }),
            'college': forms.Select(attrs={
                'class': 'block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6',
                'data-url': '/core/api/colleges/'
            }),
            'branch': forms.Select(attrs={
                'class': 'block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6',
                'data-url': '/core/api/branches/'
            }),
            'city': forms.Select(attrs={
                'class': 'block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6',
                'data-url': '/core/api/cities/'
            }),
            'state': forms.Select(attrs={
                'class': 'block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6',
                'data-url': '/core/api/states/'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize choices for foreign keys to allow validation if data is present
        # but for AJAX select2/custom implementation, we might need to handle this dynamically.
        # For now, we'll populate with all objects or handle it in the view/template.
        # However, for performance with large datasets, we shouldn't load all.
        # But since we have dummy data (10 rows), it's fine to load all for now.
        from core.models import College, Branch, City, State
        self.fields['college'].queryset = College.objects.all()
        self.fields['branch'].queryset = Branch.objects.all()
        self.fields['city'].queryset = City.objects.all()
        self.fields['state'].queryset = State.objects.all()

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if mobile:
            # Remove any non-digit characters
            mobile = ''.join(filter(str.isdigit, mobile))
            
            # Check length (assuming Indian mobile numbers)
            if len(mobile) != 10:
                raise ValidationError("Mobile number must be 10 digits.")
                
            # Check if mobile already exists (excluding current user)
            if self.instance.pk and CustomUser.objects.filter(mobile=mobile).exclude(pk=self.instance.pk).exists():
                raise ValidationError("This mobile number is already registered.")
                
        return mobile

