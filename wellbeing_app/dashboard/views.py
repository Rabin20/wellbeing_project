from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from wellbeing_app.models import MoodEntry, JournalEntry, Affirmation, FavoriteAffirmation
from .utils import calculate_streak

@login_required
def dashboard_home(request):
    # Mood data
    mood_entries = MoodEntry.objects.filter(user=request.user).order_by('-date')[:7]
    
    # Journal data
    journal_entries = JournalEntry.objects.filter(user=request.user).order_by('-date')[:3]
    
    # Affirmation data
    affirmation = Affirmation.objects.order_by('?').first()
    favorites = FavoriteAffirmation.objects.filter(user=request.user)
    
    context = {
        'mood_data': {
            'entries': mood_entries,
            'streak': calculate_streak(mood_entries),
            'chart_data': prepare_mood_chart_data(mood_entries)
        },
        'journal_data': {
            'entries': journal_entries
        },
        'affirmation_data': {
            'affirmation': affirmation,
            'is_favorite': affirmation.id in [f.affirmation_id for f in favorites] if affirmation else False
        },
        'quick_actions': [
            {'name': 'Log Mood', 'url': 'mood_tracker', 'icon': '😊'},
            {'name': 'New Journal', 'url': 'journal_add', 'icon': '📝'},
            {'name': 'Affirmations', 'url': 'affirmations', 'icon': '💖'},
            {'name': 'Get Help', 'url': 'helpline', 'icon': '🆘'}
        ]
    }
    return render(request, 'dashboard/home.html', context)

def prepare_mood_chart_data(entries):
    mood_map = {'happy': 5, 'calm': 4, 'neutral': 3, 'anxious': 2, 'sad': 1, 'angry': 0}
    return {
        'labels': [e.date.strftime('%a %d') for e in entries],
        'data': [mood_map.get(e.mood, 3) for e in entries]
    }