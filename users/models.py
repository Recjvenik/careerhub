from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager

class CustomUser(AbstractUser):
    username = None
    mobile = models.CharField(_('mobile number'), max_length=15, unique=True)
    email = models.EmailField(_('email address'), unique=True, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=20, blank=True, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    college = models.ForeignKey('core.College', on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey('core.City', on_delete=models.SET_NULL, null=True, blank=True)
    state = models.ForeignKey('core.State', on_delete=models.SET_NULL, null=True, blank=True)
    language_pref = models.CharField(max_length=10, default='en')
    is_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    def __str__(self):
        return self.mobile

class OTP(models.Model):
    mobile = models.CharField(max_length=15)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.mobile} - {self.otp}"
