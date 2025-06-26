from wellbeing_app.models import Affirmation, FavoriteAffirmation

def get_affirmation_context(user):
    affirmation = Affirmation.objects.order_by('?').first()
    favorites = set(FavoriteAffirmation.objects.filter(
        user=user
    ).values_list('affirmation_id', flat=True))
    
    return {
        'affirmation': affirmation,
        'is_favorite': affirmation.id in favorites if affirmation else False
    }