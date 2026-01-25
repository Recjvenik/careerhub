from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Question, Assessment, UserResponse, CareerPath
import json

@login_required
def start_assessment(request):
    user = request.user
    # Check profile completion - use _id fields for ForeignKey to avoid extra DB queries
    required_fields = ['full_name', 'email', 'mobile', 'college_id', 'branch_id', 'city_id', 'state_id']
    if not all(getattr(user, field) for field in required_fields):
        messages.warning(request, "Please complete your profile before starting the assessment.")
        return redirect('profile')
    Assessment.objects.filter(user=user, status='completed').delete()
    # Check if assessment already taken
    if Assessment.objects.filter(user=user, status='completed').exists():
        messages.info(request, "You have already completed the assessment.")
        return redirect('dashboard')

    if request.method == 'POST':
        # Clear previous incomplete assessments? Or just create new one.
        Assessment.objects.filter(user=user, status='incomplete').delete()
        # For now, create new.
        assessment = Assessment.objects.create(user=request.user)
        return redirect('question_view', assessment_id=assessment.id, question_index=0)
    return render(request, 'assessments/start.html')

@login_required
def question_view(request, assessment_id, question_index):
    assessment = get_object_or_404(Assessment, id=assessment_id, user=request.user)
    questions = Question.objects.filter(category='technical')[:10] # Filter by category if needed
    print('questions: ', questions.values())

    if question_index >= len(questions):
        print('question_index >= len(questions)', question_index, len(questions))
        return redirect('submit_assessment', assessment_id=assessment.id)
        
    question = questions[question_index]
    
    if request.method == 'POST':
        selected_option = request.POST.get('option')
        UserResponse.objects.create(
            assessment=assessment,
            question=question,
            selected_option=selected_option
        )
        return redirect('question_view', assessment_id=assessment.id, question_index=question_index + 1)

    return render(request, 'assessments/question.html', {
        'assessment': assessment,
        'question': question,
        'index': question_index,
        'total': len(questions)
    })

@login_required
def submit_assessment(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id, user=request.user)
    if assessment.status == 'completed':
         return redirect('assessment_result', assessment_id=assessment.id)

    assessment.status = 'completed'
    
    # 1. Calculate Score & Skill Accuracy
    responses = assessment.responses.all()
    total_score = 0
    skill_accuracy = {} # {skill_tag: {correct: 0, total: 0}}

    for response in responses:
        question = response.question
        skill = question.skill_tag
        
        if skill not in skill_accuracy:
            skill_accuracy[skill] = {'correct': 0, 'total': 0}
        
        skill_accuracy[skill]['total'] += 1
        
        if response.selected_option == question.correct_option:
            total_score += 10 # Simple scoring
            skill_accuracy[skill]['correct'] += 1
            
    assessment.score = total_score
    
    # Compute percentage per skill
    computed_skills = {}
    for skill, data in skill_accuracy.items():
        if data['total'] > 0:
            computed_skills[skill] = int((data['correct'] / data['total']) * 100)
        else:
            computed_skills[skill] = 0
            
    # 2. Match Career Path
    career_paths = CareerPath.objects.order_by('min_score')
    recommended_career = None
    
    target_career = None
    for cp in career_paths:
        if total_score < cp.min_score:
            target_career = cp
            break
            
    if not target_career:
        target_career = career_paths.last()
        
    recommended_career = target_career
    
    # 3. Confidence Band
    max_possible_score = len(responses) * 10 if responses else 60
    percentage_score = int((total_score / max_possible_score) * 100) if max_possible_score > 0 else 0
    
    confidence_band = ""
    confidence_message = ""
    
    if percentage_score < 40:
        confidence_band = "Beginner"
        confidence_message = "You have the interest, but need strong foundations. Start step by step."
    elif percentage_score < 70:
        confidence_band = "Career Ready"
        confidence_message = "You are on the right path. With focused learning, you can become job-ready."
    else:
        confidence_band = "Strong Match"
        confidence_message = "You already match this career well. Strengthen advanced skills to stand out."

    # 4. Identify Skill Gaps
    required_skills = recommended_career.required_skills if recommended_career else []
    skill_gaps = []
    
    for req_skill in required_skills:
        acc = computed_skills.get(req_skill, 0)
        if acc < 60:
            skill_gaps.append(req_skill)
            
    # 5. Recommend Courses (Updated Logic)
    # Find courses that cover the missing skills via CourseBundle model
    # We need to import CourseBundle here or at top (it's imported inside result view currently)
    from courses.models import CourseBundle
    from django.db.models import Q
    
    recommended_courses = []
    
    if skill_gaps:
        # Find courses that have ANY of the missing skills
        query = Q()
        for skill in skill_gaps:
            query |= Q(skills_required__icontains=skill)
            
        courses = CourseBundle.objects.filter(query, is_active=True).distinct()
        
        for course in courses:
            recommended_courses.append({
                'title': course.career_title,
                'course_id': course.id,
                'slug': course.slug
            })
            
    # Save Result Data
    result_data = {
        'career': recommended_career.title if recommended_career else "N/A",
        'confidence_band': confidence_band,
        'confidence_message': confidence_message,
        'skill_gaps': skill_gaps,
        'recommended_courses': recommended_courses,
        'skill_accuracy': computed_skills,
        'percentage_score': percentage_score
    }
    
    assessment.result_data = result_data
    assessment.save()
    
    return redirect('assessment_result', assessment_id=assessment.id)

@login_required
def assessment_result(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id, user=request.user)
    
    # Fetch course bundles matching user's degree
    # Fetch course bundles matching user's degree
    from courses.models import CourseBundle, Enrollment
    course_bundles = []
    print('request.user.degree: ', request.user.degree)
    if request.user.degree:
        course_bundles = CourseBundle.objects.filter(
            degrees=request.user.degree,
            is_active=True
        ).distinct()
        
    active_enrollment = Enrollment.objects.filter(user=request.user, status='active').first()
    active_course_bundle_id = active_enrollment.course.id if active_enrollment else None
    
    return render(request, 'assessments/result.html', {
        'assessment': assessment,
        'result': assessment.result_data,
        'course_bundles': course_bundles,
        'active_course_bundle_id': active_course_bundle_id,
    })

