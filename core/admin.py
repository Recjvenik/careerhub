from django.contrib import admin
from .models import State, City, CityState, College, Branch, Degree

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(CityState)
class CityStateAdmin(admin.ModelAdmin):
    list_display = ['city', 'state']
    search_fields = ['city__name', 'state__name']

@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name']
    search_fields = ['name', 'short_name']

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name']
    search_fields = ['name', 'short_name']

@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    list_display = ['name', 'full_name', 'category']
    search_fields = ['name', 'full_name']
    list_filter = ['category']
