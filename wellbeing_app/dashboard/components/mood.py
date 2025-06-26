from datetime import timedelta
from django.utils import timezone
from wellbeing_app.models import MoodEntry

def calculate_streak(entries):
    """Calculate consecutive day streak from sorted entries"""
    if not entries:
        return 0
    
    streak = 1
    current_date = entries[0].date.date()
    
    for entry in entries[1:]:
        entry_date = entry.date.date()
        if (current_date - entry_date).days == 1:
            streak += 1
            current_date = entry_date
        else:
            break
    
    return streak