from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Question, Assessment, UserResponse
from recommendations.logic import get_recommendations

@login_required
def start_assessment(request):
    if request.method == 'POST':
        assessment = Assessment.objects.create(user=request.user)
        return redirect('question_view', assessment_id=assessment.id, question_index=0)
    return render(request, 'assessments/start.html')

@login_required
def question_view(request, assessment_id, question_index):
    assessment = get_object_or_404(Assessment, id=assessment_id, user=request.user)
    questions = Question.objects.all()
    
    if question_index >= len(questions):
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
    assessment.status = 'completed'
    
    # Calculate score (simple logic for now)
    score = 0
    responses = assessment.responses.all()
    for response in responses:
        if response.selected_option == response.question.correct_option:
            score += 10
            
    assessment.score = score
    assessment.save()
    
    return redirect('assessment_result', assessment_id=assessment.id)

@login_required
def assessment_result(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id, user=request.user)
    recommendations = get_recommendations(assessment)
    
    return render(request, 'assessments/result.html', {
        'assessment': assessment,
        'recommendations': recommendations
    })
