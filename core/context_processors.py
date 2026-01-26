from django.conf import settings

def settings_context(request):
    """
    Exposes specific settings to all templates.
    """
    return {
        'FREE_ALL_COURSES': getattr(settings, 'FREE_ALL_COURSES', False)
    }
