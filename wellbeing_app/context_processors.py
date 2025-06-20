def language_processor(request):
    return {
        'current_language': request.session.get('language', 'en'),
        'available_languages': ['en', 'mi']  # Hardcoded language options
    }