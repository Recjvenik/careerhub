from django.db import models
from users.models import CustomUser

class CareerPath(models.Model):
    career_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    min_score = models.IntegerField()
    required_skills = models.JSONField(help_text="List of required skills")

    def __str__(self):
        return self.title

    def __str__(self):
        return self.title

class Question(models.Model):
    CATEGORY_CHOICES = (
        ('psychometric', 'Psychometric'),
        ('aptitude', 'Aptitude'),
        ('technical', 'Technical'),
    )
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )
    text = models.TextField()
    options = models.JSONField(help_text="List of options")
    correct_option = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='technical')
    skill_tag = models.CharField(max_length=100, blank=True, null=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    
    def __str__(self):
        return self.text[:50]

class Assessment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_taken = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='pending') # pending, completed
    result_data = models.JSONField(default=dict, blank=True) # Stores the computed analysis

    def __str__(self):
        return f"{self.user.mobile} - {self.date_taken}"

class UserResponse(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.assessment.id} - {self.question.id}"
