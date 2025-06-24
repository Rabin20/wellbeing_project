from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from wellbeing_app import views
from wellbeing_app.views import DailyAffirmationsView, MoodHistoryView, HelplineView, FavoriteAffirmationsView, save_affirmation


# Non-translated URLs (admin and language APIs)
urlpatterns = i18n_patterns(
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),  # Django's built-in language switcher
    
    # Translation API endpoints (not language-prefixed)
    path('api/translate/', views.translate_bulk, name='translate_bulk'),
    path('api/set-language/', views.set_language_ajax, name='set_language_ajax'),
    path('affirmations/', DailyAffirmationsView.as_view(), name='affirmations'),
    path('affirmations/favorites/', FavoriteAffirmationsView.as_view(), name='favorite_affirmations'),
    path('affirmations/save/', save_affirmation, name='save_affirmation'),
    path('mood-history/', MoodHistoryView.as_view(), name='mood_history'),
    path('helpline/', HelplineView.as_view(), name='helpline'),
    prefix_default_language=False
)

# Language-prefixed URLs (all frontend routes)
urlpatterns += i18n_patterns(
    # Core pages
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    
    # Mood tracking
    path('mood/', views.mood_tracker, name='mood_tracker'),
    path('mood/history/', views.mood_history, name='mood_history'),
    
    # Journal
    path('journal/', views.journal_list, name='journal_list'),
    path('journal/add/', views.journal_add, name='journal_add'),
    
    # Authentication
    path('accounts/', include('django.contrib.auth.urls')),
    
    prefix_default_language=False
)

