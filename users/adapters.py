from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email
from .models import CustomUser


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for social account signups.
    Handles the case where users sign up via Google without a mobile number.
    """
    
    def pre_social_login(self, request, sociallogin):
        """
        If a user with this email already exists, connect the social account to it.
        """
        if sociallogin.is_existing:
            return
        
        # Get email from social account
        email = user_email(sociallogin.user)
        if not email:
            return
        
        # Check if user with this email exists
        try:
            existing_user = CustomUser.objects.get(email__iexact=email)
            # Connect the social account to the existing user
            sociallogin.connect(request, existing_user)
        except CustomUser.DoesNotExist:
            pass
    
    def save_user(self, request, sociallogin, form=None):
        """
        Save the user created from social login.
        We need to handle the case where mobile is the USERNAME_FIELD but it's not provided.
        """
        user = sociallogin.user
        
        # Extract data from social account
        extra_data = sociallogin.account.extra_data
        
        # Set email from social account
        email = extra_data.get('email', '')
        user.email = email
        
        # Set full name from social account
        name = extra_data.get('name', '')
        user.full_name = name
        
        # Set first_name and last_name if available
        user.first_name = extra_data.get('given_name', '')
        user.last_name = extra_data.get('family_name', '')
        
        # Mobile will be null for Google signups - that's okay
        user.mobile = None
        
        # Mark as verified since Google verified the email
        user.is_verified = True
        
        # Set unusable password since they're using social login
        user.set_unusable_password()
        
        user.save()
        
        return user
