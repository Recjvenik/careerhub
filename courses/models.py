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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.IntegerField(default=0, help_text="Percentage completed")
    
    def __str__(self):
        return f"{self.user.mobile} - {self.course.title}"
