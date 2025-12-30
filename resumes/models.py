from django.db import models
from users.models import CustomUser

class Resume(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/')
    ats_score = models.IntegerField(default=0)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Resume of {self.user.mobile}"
