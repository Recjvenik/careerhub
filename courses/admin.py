from django.contrib import admin
from .models import Enrollment, CourseBundle

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'enrolled_at', 'progress', 'status']
    list_filter = ['status']
    search_fields = ['user__email', 'course__career_title']

@admin.register(CourseBundle)
class CourseBundleAdmin(admin.ModelAdmin):
    list_display = ['career_title', 'duration', 'original_price', 'discounted_price', 'next_batch_date', 'is_active']
    search_fields = ['career_title', 'skills_required']
    list_filter = ['is_active', 'degrees']
    filter_horizontal = ['degrees']
    prepopulated_fields = {'slug': ('career_title',)}
