from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Enrollment

@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    user = request.user
    
    # Check for existing active enrollment
    active_enrollment = Enrollment.objects.filter(user=user, status='active').first()
    
    if active_enrollment:
        if active_enrollment.course == course:
            messages.info(request, "You are already enrolled in this course.")
            return redirect('dashboard')
        else:
            # Prompt to change course
            return render(request, 'courses/confirm_change.html', {
                'current_course': active_enrollment.course,
                'new_course': course
            })
            
    # Create new enrollment
    Enrollment.objects.create(user=user, course=course, status='active')
    messages.success(request, f"Successfully enrolled in {course.title}!")
    return redirect('dashboard')

@login_required
def change_course(request, slug):
    if request.method != 'POST':
        return redirect('course_detail', slug=slug)
        
    course = get_object_or_404(Course, slug=slug)
    user = request.user
    
    # Deactivate current active enrollment
    active_enrollment = Enrollment.objects.filter(user=user, status='active').first()
    if active_enrollment:
        active_enrollment.status = 'dropped'
        active_enrollment.save()
        
    # Create new enrollment
    Enrollment.objects.create(user=user, course=course, status='active')
    messages.success(request, f"Course changed to {course.title}!")
    return redirect('dashboard')

def course_list(request):
    courses = Course.objects.filter(is_active=True)
    active_enrollment_course_id = None
    
    if request.user.is_authenticated:
        active_enrollment = Enrollment.objects.filter(user=request.user, status='active').first()
        if active_enrollment:
            active_enrollment_course_id = active_enrollment.course.id
            
    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'active_course_id': active_enrollment_course_id
    })
