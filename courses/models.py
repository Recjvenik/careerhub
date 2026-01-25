from django.db import models
from users.models import CustomUser

from django.utils.text import slugify

class Course(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.TextField(blank=True)
    description = models.TextField()
    duration = models.CharField(max_length=50, help_text="e.g. 4 weeks")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    original_price_inr = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    level = models.CharField(max_length=50, default='Beginner')
    language = models.JSONField(default=list)  # e.g. ["English", "Hindi"]
    programs_included = models.JSONField(default=list)
    ideal_for = models.JSONField(default=list)
    job_roles = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.IntegerField(default=0, help_text="Percentage completed")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    def __str__(self):
        return f"{self.user.mobile} - {self.course.title} ({self.status})"

class CourseSkill(models.Model):
    COVERAGE_CHOICES = (
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='skills')
    skill_tag = models.CharField(max_length=100)
    coverage_level = models.CharField(max_length=20, choices=COVERAGE_CHOICES, default='basic')
    relevance_score = models.IntegerField(default=100)
    
    class Meta:
        unique_together = ['course', 'skill_tag']
    
    def __str__(self):
        return f"{self.course.title} - {self.skill_tag} ({self.coverage_level})"

class CourseBundle(models.Model):
    career_title = models.CharField(max_length=255)  # "Business Development Executive"
    skills_required = models.TextField()  # Semicolon-separated skills
    duration = models.CharField(max_length=50)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    next_batch_date = models.DateField()
    initial_salary = models.IntegerField(default=0)  # Average initial salary
    degrees = models.ManyToManyField('core.Degree', related_name='course_bundles')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.career_title

    def get_skills_list(self):
        return [s.strip() for s in self.skills_required.split(';')]

