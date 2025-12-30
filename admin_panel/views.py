from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from users.models import CustomUser
from assessments.models import Assessment

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def dashboard(request):
    total_users = CustomUser.objects.count()
    total_assessments = Assessment.objects.count()
    completed_assessments = Assessment.objects.filter(status='completed').count()
    
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]
    
    return render(request, 'admin_panel/dashboard.html', {
        'total_users': total_users,
        'total_assessments': total_assessments,
        'completed_assessments': completed_assessments,
        'recent_users': recent_users
    })
