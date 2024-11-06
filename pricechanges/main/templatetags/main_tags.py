from django import template
from main.models import Marketplace, TagItem

register = template.Library()

@register.inclusion_tag('main/list_menu.html')
def show_menu(menu_select=0):
    menu = Marketplace.objects.all()
    return {'menu': menu, 'menu_select': menu_select}

@register.inclusion_tag('main/list_tags.html')
def show_tags():
    return {'tags': TagItem.objects.all()}

@register.inclusion_tag('main/nav.html')
def show_nav():
    nav = [
        {'title': "О сайте", 'url_name': 'about'},
        {'title': "Обратная связь", 'url_name': 'contact'},
        {'title': "Войти", 'url_name': 'login'}
    ]
    return {'nav': nav}
