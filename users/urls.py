from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('verify-registration-otp/', views.verify_registration_otp, name='verify_registration_otp'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),
    path('login/', views.login_view, name='login'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
]
