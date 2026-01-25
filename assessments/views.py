from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Question, Assessment, UserResponse, CareerPath
import json
import random
from collections import defaultdict

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
        # Clear previous incomplete assessments
        Assessment.objects.filter(user=user, status='pending').delete()
        
        # Determine Degree Type (Tech vs Non-Tech)
        is_tech = False
        if hasattr(user, 'degree') and user.degree:
            is_tech = user.degree.is_tech
            
        all_qs = list(Question.objects.all())

        by_category = defaultdict(list)
        for q in all_qs:
            by_category[q.category].append(q)

        def pick(cat, n):
            qs = by_category.get(cat, [])
            return qs if len(qs) <= n else random.sample(qs, n)

        if is_tech:
            questions = (
                pick('technical', 4) +
                pick('aptitude', 1) +
                pick('psychometric', 2)
            )
        else:
            questions = (
                pick('aptitude', 2) +
                pick('psychometric', 5)
            )

        random.shuffle(questions)
        question_ids = [q.id for q in questions]
        
        assessment = Assessment.objects.create(user=request.user, question_order=question_ids)
        return redirect('question_view', assessment_id=assessment.id, question_index=0)
    return render(request, 'assessments/start.html')

@login_required
def question_view(request, assessment_id, question_index):
    assessment = get_object_or_404(Assessment, id=assessment_id, user=request.user)
    
    question_ids = assessment.question_order
    total_questions = len(question_ids)
    
    if question_index >= total_questions:
        return redirect('submit_assessment', assessment_id=assessment.id)
        
    # Get current question ID
    try:
        question_id = question_ids[question_index]
    except IndexError:
        return redirect('submit_assessment', assessment_id=assessment.id)
        
    question = get_object_or_404(Question, id=question_id)
    
    if request.method == 'POST':
        selected_option = request.POST.get('option')
        # Update or create response
        UserResponse.objects.update_or_create(
            assessment=assessment,
            question=question,
            defaults={'selected_option': selected_option}
        )
        return redirect('question_view', assessment_id=assessment.id, question_index=question_index + 1)

    return render(request, 'assessments/question.html', {
        'assessment': assessment,
        'question': question,
        'index': question_index,
        'total': total_questions
    })

@login_required
def submit_assessment(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id, user=request.user)
    if assessment.status == 'completed':
         return redirect('assessment_result', assessment_id=assessment.id)

    assessment.status = 'completed'
    responses = assessment.responses.all()

    # --- New Analysis Logic ---
    tech_correct = 0
    tech_total = 0
    apt_correct = 0
    apt_total = 0
    
    # Psychometric Counts
    psych_profile_traits = []
    
    # Mapping Data (Text to Trait Logic)
    # Using normalized keys (first few words) strictly matching provided JSON
    PSYCH_MAPPING = {
        "Which activity do you enjoy more": {
            "A": "Analytical Thinking",
            "B": "Verbal & Creative",
            "C": "Social & Empathetic"
        },
        "How do you prefer to work": {
            "A": "Independent Work Style",
            "B": "Collaborative Work Style"
        },
        "How do you feel about unclear instructions": {
            "A": "Explorative / Ambiguity Tolerant",
            "B": "Structured / Process Driven"
        },
        "Which tools are you most comfortable with": {
            "A": "Business & Operations",
            "B": "Communication & Content",
            "C": "Technical & Data"
        },
        "When learning something new, you prefer": {
            "A": "Hands-on Learner",
            "B": "Theoretical Learner",
            "C": "Social Learner"
        }
    }

    for response in responses:
        q = response.question
        category = q.category
        selected = response.selected_option

        if category == 'technical':
            tech_total += 1
            if selected == q.correct_option:
                tech_correct += 1
        elif category == 'aptitude':
            apt_total += 1
            if selected == q.correct_option:
                apt_correct += 1
        elif category == 'psychometric':
            # Match question text prefix
            q_text_clean = q.text.strip().rstrip('?.:')
            found_map = None
            for key, val in PSYCH_MAPPING.items():
                if key in q_text_clean:
                    found_map = val
                    break
            
            if found_map:
                trait = found_map.get(selected)
                if trait:
                    psych_profile_traits.append(trait)

    # Pad Tech attributes (since they answer fewer psych questions)
    if tech_total > 0:
        # Tech users get these by default to show a fuller profile
        extras = ["Technical Proficiency", "Problem Solving"]
        for e in extras:
            if e not in psych_profile_traits:
                psych_profile_traits.append(e)

    # Tech Analysis (Enforce Min 70%)
    raw_tech = int((tech_correct / tech_total) * 100) if tech_total > 0 else 0
    tech_score = max(raw_tech, 70) if tech_total > 0 else 0
    
    # Aptitude Analysis (Enforce Min 70%)
    raw_apt = int((apt_correct / apt_total) * 100) if apt_total > 0 else 0
    apt_score = max(raw_apt, 70) if apt_total > 0 else 0

    # Total Score
    scored_total = tech_total + apt_total
    scored_correct = tech_correct + apt_correct
    raw_total = int((scored_correct / scored_total) * 100) if scored_total > 0 else 0
    total_score_pct = max(raw_total, 70) if scored_total > 0 else 0
    
    assessment.score = total_score_pct

    result_data = {
        'tech_score': tech_score,
        'tech_total': tech_total,
        'apt_score': apt_score,
        'apt_total': apt_total,
        'psych_profile': psych_profile_traits,
        'total_score': total_score_pct
    }
    
    assessment.result_data = result_data
    assessment.save()
    
    return redirect('assessment_result', assessment_id=assessment.id)

    # --- Old Logic (Commented Out) ---
    '''
    # 1. Calculate Score & Skill Accuracy
    responses = assessment.responses.all()
    total_score = 0
    skill_accuracy = {} # {skill_tag: {correct: 0, total: 0}}
    # ... (rest of old code)
    '''

@login_required
def assessment_result(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id, user=request.user)
    
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
    print('assessment.result_data: ', assessment.result_data)
    return render(request, 'assessments/result.html', {
        'assessment': assessment,
        'result': assessment.result_data,
        'course_bundles': course_bundles,
        'active_course_bundle_id': active_course_bundle_id,
    })

