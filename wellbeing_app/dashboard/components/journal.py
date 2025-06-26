from wellbeing_app.models import JournalEntry
def get_journal_context(user):
    entries = JournalEntry.objects.filter(
        user=user
    ).order_by('-date')[:3]  # Last 3 entries
    
    return {
        'entries': entries,
        'count': entries.count()
    }