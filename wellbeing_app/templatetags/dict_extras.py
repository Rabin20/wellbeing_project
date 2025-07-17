from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Return value from a dict for the provided key."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None