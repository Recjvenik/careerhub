from django.shortcuts import render
from assessments.models import Assessment

def index(request):
    assessment_completed = False
    if request.user.is_authenticated:
        assessment_completed = Assessment.objects.filter(user=request.user, status='completed').exists()
        
    return render(request, 'landing/index.html', {
        'assessment_completed': assessment_completed
    })
