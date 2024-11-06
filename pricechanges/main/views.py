from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from .models import Items, Marketplace, TagItem


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
        'data_item': data_item,
        'menu_selected': 0,
    }
    return render(request, 'main/index.html', context=data)


def about(request):
    return render(request, 'main/about.html', {'title': 'О сайте'})


def show_item(request, item_slug):
    item = get_object_or_404(Items, slug=item_slug)
    data = {
        'title': item.name,
        'item': item,
        'menu_selected': 1,
    }
    return render(request, 'main/item.html', context=data)

def show_menu(request, mtplace_slug):
    marketplace = get_object_or_404(Marketplace, slug=mtplace_slug)
    items_mtplace = Items.actual.filter(mtplace_id=marketplace.pk)
    print(items_mtplace)

    data = {
        'title': f'Маркетплейс: {marketplace.name}',
        'data_item': items_mtplace,
        'menu_selected': marketplace.pk,
    }
    return render(request, 'main/index.html', context=data)

def show_tag_items(request, tag_slug):
    tag = get_object_or_404(TagItem, slug=tag_slug)
    items_tag = tag.items.all()

    data = {
        'title': f'Товары по тегу: {tag.tag}',
        'data_item': items_tag,
        'menu_selected': None,
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
