from django import template
import main.views as views

register = template.Library()


@register.simple_tag()
def get_menu():
    return views.menu
@register.inclusion_tag('main/list_menu.html')
def show_menu(menu_select=0):
    menu = views.menu
    return {'menu': menu, 'menu_select': menu_select}