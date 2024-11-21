from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.views.generic import TemplateView, ListView, DetailView

from .forms import AddItemForm
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

class HomeItems(ListView):
    model = Items
    template_name = 'main/index.html'
    context_object_name = 'data_item'
    extra_context = {
        'title': 'Главная страница',
        'menu_selected': 0,
    }

    def get_queryset(self):
        return Items.actual.all().select_related('mtplace')

def about(request):
    return render(request, 'main/about.html', {'title': 'О сайте'})


def show_item(request, item_slug):
    item = get_object_or_404(Items, slug=item_slug)
    data = {
        'title': item.name,
        'item': item,
        'menu_selected': 0,
    }
    return render(request, 'main/item.html', context=data)

class ShowItem(DetailView):
    model = Items
    template_name = 'main/item.html'
    slug_url_kwarg = 'item_slug'
    context_object_name = 'item'
    '''ДОДЕЛАТЬ'''


def show_menu(request, mtplace_slug):
    marketplace = get_object_or_404(Marketplace, slug=mtplace_slug)
    items_mtplace = Items.actual.filter(mtplace_id=marketplace.pk).select_related('mtplace')
    print(items_mtplace)

    data = {
        'title': f'Маркетплейс: {marketplace.name}',
        'data_item': items_mtplace,
        'menu_selected': marketplace.pk,
    }
    return render(request, 'main/index.html', context=data)

def show_tag_items(request, tag_slug):
    tag = get_object_or_404(TagItem, slug=tag_slug)
    items_tag = tag.items.all().select_related('mtplace')

    data = {
        'title': f'Товары по тегу: {tag.tag}',
        'data_item': items_tag,
        'menu_selected': None,
    }
    return render(request, 'main/index.html', context=data)


def add_item(request):
    if request.method == 'POST':
        form = AddItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AddItemForm()

    data = {
        'title': 'Добавление товара с маркетплейса',
        'form': form
    }
    return render(request, 'main/add_item.html', data)


def contact(request):
    return HttpResponse("Обратная связь")


def login(request):
    return HttpResponse("Авторизация")


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")
