from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify

menu = [{'title': "О сайте", 'url_name': 'about'},
        {'title': "Обратная связь", 'url_name': 'contact'},
        {'title': "Войти", 'url_name': 'login'}
]

data_item = [
    {'id': 1, 'title': 'Рубашка', 'content': '''<h1>Рубашка белая</h1>''',
     'is_published': True},
    {'id': 2, 'title': 'Носки черные', 'content': 'Носки черные', 'is_published': True},
    {'id': 3, 'title': 'Пуфик красный', 'content': 'Пуфик красный', 'is_published': True},
]


def index(request):
    data = {
        'title': 'Главная страница',
        'menu': menu,
        'data_item': data_item,
    }
    return render(request, 'main/index.html', context=data)


def about(request):
    return render(request, 'main/about.html', {'title': 'О сайте', 'menu': menu})


def show_item(request, item_id):
    return HttpResponse(f"Отображение статьи с id = {item_id}")


def addpage(request):
    return HttpResponse("Добавление статьи")


def contact(request):
    return HttpResponse("Обратная связь")


def login(request):
    return HttpResponse("Авторизация")


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")
