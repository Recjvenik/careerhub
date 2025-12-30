from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.start_assessment, name='start_assessment'),
    path('<int:assessment_id>/question/<int:question_index>/', views.question_view, name='question_view'),
    path('<int:assessment_id>/submit/', views.submit_assessment, name='submit_assessment'),
    path('<int:assessment_id>/result/', views.assessment_result, name='assessment_result'),
]
