from django import template

register = template.Library()

@register.filter(name='yesno')
def yesno(value):
    if value:
        return 'Yes'
    return 'No'