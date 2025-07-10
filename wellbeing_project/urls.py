from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static

from wellbeing_app import views
from wellbeing_app.views import (
    DailyAffirmationsView, HelplineView, FavoriteAffirmationsView,
    save_affirmation, mood_history
)
from wellbeing_app.admin import wellbeing_admin

# Non-language-prefixed backend/admin/API routes
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('dashboard/', wellbeing_admin.urls),
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/translate/', views.translate_bulk, name='translate_bulk'),
    path('api/set-language/', views.set_language_ajax, name='set_language_ajax'),

    # Journal reactions and uploads
    path('journal/<int:pk>/react/', views.react_to_journal, name='journal_react'),
    path('upload-journal-image/', views.upload_journal_image, name='upload_journal_image'),
]

# Language-prefixed frontend routes
urlpatterns += i18n_patterns(
    # Core pages
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),

    # Mood tracking
    path('mood/', views.mood_tracker, name='mood_tracker'),
    path('mood/history/', views.mood_history, name='mood_history'),

    # Mood edit/delete
    path('mood/edit/<int:pk>/', views.mood_edit, name='mood_edit'),
    path('mood/delete/<int:pk>/', views.mood_delete, name='mood_delete'),

    # Journal
    path('journal/', views.journal_list, name='journal_list'),
    path('journal/add/', views.journal_add, name='journal_add'),
    path('journal/edit/<int:pk>/', views.journal_edit, name='journal_edit'),
    path('journal/delete/<int:pk>/', views.journal_delete, name='journal_delete'),
    path('upload-journal-image/', views.upload_journal_image, name='upload_journal_image'),

    # Affirmations
    path('affirmations/', DailyAffirmationsView.as_view(), name='affirmations'),
    path('affirmations/favorites/', FavoriteAffirmationsView.as_view(), name='favorite_affirmations'),
    path('affirmations/save/', save_affirmation, name='save_affirmation'),

    # Helpline
    path('helpline/', HelplineView.as_view(), name='helpline'),

    # Auth
    path('accounts/', include('django.contrib.auth.urls')),

    prefix_default_language=False
)

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
