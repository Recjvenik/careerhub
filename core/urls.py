from django.urls import path
from . import views

urlpatterns = [
    path('api/states/', views.search_states, name='search_states'),
    path('api/cities/', views.search_cities, name='search_cities'),
    path('api/colleges/', views.search_colleges, name='search_colleges'),
    path('api/branches/', views.search_branches, name='search_branches'),
]
