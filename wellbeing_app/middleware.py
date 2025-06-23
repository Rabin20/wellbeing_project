from django.utils import translation

class ForceLangMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang_code = request.session.get('django_language')
        if lang_code:
            translation.activate(lang_code)
        return self.get_response(request)