from django.contrib import admin
from .models import Course, Enrollment, CourseSkill, CourseBundle

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'duration', 'price', 'level', 'is_active']
    search_fields = ['title', 'description']
    list_filter = ['level', 'is_active']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'enrolled_at', 'progress', 'status']
    list_filter = ['status']
    search_fields = ['user__email', 'course__title']

@admin.register(CourseSkill)
class CourseSkillAdmin(admin.ModelAdmin):
    list_display = ['course', 'skill_tag', 'coverage_level', 'relevance_score']
    list_filter = ['coverage_level']
    search_fields = ['skill_tag', 'course__title']

@admin.register(CourseBundle)
class CourseBundleAdmin(admin.ModelAdmin):
    list_display = ['career_title', 'duration', 'original_price', 'discounted_price', 'next_batch_date', 'is_active']
    search_fields = ['career_title', 'skills_required']
    list_filter = ['is_active', 'degrees']
    filter_horizontal = ['degrees']
