from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list_view, name='course_list'),
    path('<slug:slug>/enroll/', views.enroll_course_view, name='enroll_course'),
]
