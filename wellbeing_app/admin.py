from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.contrib.auth.models import User, Group
from .models import MoodEntry, JournalEntry, Affirmation, FavoriteAffirmation
from django.template.response import TemplateResponse
from django.shortcuts import redirect

class WellbeingAdminSite(admin.AdminSite):
    site_header = "Wellbeing Dashboard"
    site_title = "Wellbeing Admin"
    index_title = ""
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('mood-entries/', self.admin_view(self.mood_entries_view), name='mood_entries'),
            path('journal-entries/', self.admin_view(self.journal_entries_view), name='journal_entries'),
            path('affirmations/', self.admin_view(self.affirmations_view), name='affirmations'),
            path('users/', self.admin_view(self.users_view), name='users'),
        ]
        # Prepend custom URLs so they take precedence
        return custom_urls + urls
    
    def mood_entries_view(self, request):
        context = {
            **self.each_context(request),
            'title': 'Mood Entries',
            'mood_entries': MoodEntry.objects.all().order_by('-date'),
            'opts': MoodEntry._meta,
        }
        return TemplateResponse(request, 'admin/mood_entries.html', context)
    
    def journal_entries_view(self, request):
        context = {
            **self.each_context(request),
            'title': 'Journal Entries',
            'journal_entries': JournalEntry.objects.all().order_by('-date'),
            'opts': JournalEntry._meta,
        }
        return TemplateResponse(request, 'admin/journal_entries.html', context)
    
    def affirmations_view(self, request):
        context = {
            **self.each_context(request),
            'title': 'Affirmations',
            'affirmations': Affirmation.objects.all(),
            'opts': Affirmation._meta,
        }
        return TemplateResponse(request, 'admin/affirmations.html', context)
    
    def users_view(self, request):
        context = {
            **self.each_context(request),
            'title': 'Users',
            'users': User.objects.all().order_by('-date_joined'),
            'opts': User._meta,
        }
        return TemplateResponse(request, 'admin/users.html', context)
    
    def index(self, request, extra_context=None):
        # Redirect to mood entries by default
        return redirect('wellbeing:mood_entries')

# Create admin instance with a unique name
wellbeing_admin = WellbeingAdminSite(name='wellbeing')

# Model Admins
@admin.register(MoodEntry, site=wellbeing_admin)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'mood_display', 'date', 'notes_short')
    search_fields = ('user__username', 'notes')
    
    def mood_display(self, obj):
        icons = {'happy': '😊', 'calm': '😌', 'neutral': '😐', 'anxious': '😟', 'angry': '😠', 'sad': '😢'}
        return f"{icons.get(obj.mood, '')} {obj.get_mood_display()}"
    mood_display.short_description = 'Mood'
    
    def notes_short(self, obj):
        return obj.notes[:50] + '...' if len(obj.notes) > 50 else obj.notes
    notes_short.short_description = 'Notes'

# Register other models
wellbeing_admin.register(JournalEntry)
wellbeing_admin.register(Affirmation)
wellbeing_admin.register(FavoriteAffirmation)
wellbeing_admin.register(User)
wellbeing_admin.register(Group)