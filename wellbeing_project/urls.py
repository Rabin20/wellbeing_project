from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView
from wellbeing_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),  # Language switcher URLs
]

urlpatterns += i18n_patterns(
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('mood/', views.mood_tracker, name='mood_tracker'),
    path('history/', views.mood_history, name='mood_history'),
    path('journal/', views.journal_list, name='journal_list'),
    path('journal/add/', views.journal_add, name='journal_add'),
    path('accounts/', include('django.contrib.auth.urls')),
    prefix_default_language=True  # Makes /mi/ optional for Māori URLs
)