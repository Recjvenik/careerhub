from django.db import models
from users.models import CustomUser

from django.utils.text import slugify

from django.utils.text import slugify

class CourseBundle(models.Model):
    career_title = models.CharField(max_length=255)  # "Business Development Executive"
    slug = models.SlugField(unique=True, blank=True, null=True)
    skills_required = models.TextField()  # Semicolon-separated skills
    duration = models.CharField(max_length=50)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    next_batch_date = models.DateField()
    initial_salary = models.IntegerField(default=0)  # Average initial salary
    degrees = models.ManyToManyField('core.Degree', related_name='course_bundles')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.career_title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.career_title

    def get_skills_list(self):
        return [s.strip() for s in self.skills_required.split(';')]

    @property
    def title(self):
        """Alias for career_title to maintain compatibility with templates expecting .title"""
        return self.career_title
        
    @property
    def programs_included(self):
        """Return skills as a list for compatibility with templates expecting .programs_included"""
        return self.get_skills_list()

class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseBundle, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.IntegerField(default=0, help_text="Percentage completed")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    def __str__(self):
        return f"{self.user.mobile} - {self.course.career_title} ({self.status})"

