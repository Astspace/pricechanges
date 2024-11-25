from django import template
from main.models import Marketplace, TagItem

register = template.Library()

@register.inclusion_tag('main/list_menu.html')
def show_menu(menu_select=None):
    menu = Marketplace.objects.all()
    return {'menu': menu, 'menu_select': menu_select}

@register.inclusion_tag('main/list_tags.html')
def show_tags():
    return {'tags': TagItem.objects.all()}