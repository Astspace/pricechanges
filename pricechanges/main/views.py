from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from .models import Items

nav = [
    {'title': "О сайте", 'url_name': 'about'},
    {'title': "Обратная связь", 'url_name': 'contact'},
    {'title': "Войти", 'url_name': 'login'}
]

data_item = [
    {'id': 1, 'title': 'Рубашка', 'content': '''<h1>Рубашка белая</h1>''',
     'is_published': True},
    {'id': 2, 'title': 'Носки черные', 'content': 'Носки черные', 'is_published': True},
    {'id': 3, 'title': 'Пуфик красный', 'content': 'Пуфик красный', 'is_published': True},
]

menu = [
    {'id': 1, 'name': "Просмотр товара"},
    {'id': 2, 'name': "Редактирование товара"},
    {'id': 3, 'name': "Добавление товара"},
]

def index(request):
    data_item = Items.objects.all()
    data = {
        'title': 'Главная страница',
        'nav': nav,
        'data_item': data_item,
        'menu_selected': 0,
    }
    return render(request, 'main/index.html', context=data)


def about(request):
    return render(request, 'main/about.html', {'title': 'О сайте', 'nav': nav})


def show_item(request, item_slug):
    item = get_object_or_404(Items, slug=item_slug)
    data = {
        'title': item.name,
        'nav': nav,
        'menu': menu,
        'item': item,
        'menu_selected': 1,
    }
    return render(request, 'main/item.html', context=data)

def show_menu(request, menu_id):
    data = {
        'title': 'Главная страница',
        'nav': nav,
        'data_item': data_item,
        'menu_selected': menu_id,
    }
    return render(request, 'main/index.html', context=data)


def addpage(request):
    return HttpResponse("Добавление статьи")


def contact(request):
    return HttpResponse("Обратная связь")


def login(request):
    return HttpResponse("Авторизация")


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")
