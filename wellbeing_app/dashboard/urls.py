from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Home
    path('', views.dashboard_home, name='home'),
    
    # Mood Tracking
    path('mood/', views.mood_list, name='mood_list'),
    path('mood/add/', views.mood_add, name='mood_add'),
    
    # Journal
    path('journal/', views.journal_list, name='journal_list'),
    path('journal/add/', views.journal_add, name='journal_add'),
    
    # Affirmations
    path('affirmations/', views.affirmation_list, name='affirmation_list'),
    path('affirmations/add/', views.affirmation_add, name='affirmation_add'),
    
    # User Management (staff only)
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_add, name='user_add'),
]