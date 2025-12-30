from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Enrollment

def course_list_view(request):
    courses = Course.objects.filter(is_active=True)
    return render(request, 'courses/course_list.html', {'courses': courses})

@login_required
def enroll_course_view(request, slug):
    course = get_object_or_404(Course, slug=slug)
    
    # Check if already enrolled
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.info(request, f"You are already enrolled in {course.title}.")
        return redirect('course_list')
        
    # Create enrollment
    Enrollment.objects.create(user=request.user, course=course)
    messages.success(request, f"Successfully enrolled in {course.title}!")
    return redirect('course_list')
