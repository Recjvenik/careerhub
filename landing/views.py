from django.shortcuts import render
from assessments.models import Assessment

def is_mobile(request):
    """Detect if the request is from a mobile device"""
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    mobile_keywords = ['mobile', 'android', 'iphone', 'ipod', 'blackberry', 'windows phone']
    return any(keyword in user_agent for keyword in mobile_keywords)

def index(request):
    assessment_completed = False
    if request.user.is_authenticated:
        assessment_completed = Assessment.objects.filter(user=request.user, status='completed').exists()
    
    template = 'landing/index_mobile.html' if is_mobile(request) else 'landing/index.html'
    
    return render(request, template, {
        'assessment_completed': assessment_completed
    })
