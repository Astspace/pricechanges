from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, UpdateView

from .forms import AddItemForm
from .models import Items, Marketplace, TagItem
from .utils import DataMixin


class HomeItems(DataMixin, ListView):
    template_name = 'main/index.html'
    context_object_name = 'data_item'
    title = 'Главная страница'
    menu_selected = 0

    def get_queryset(self):
        return Items.actual.all().select_related('mtplace')


class About(DataMixin, TemplateView):
    template_name = 'main/about.html'
    title = 'О сайте'
def about(request):
    return render(request, 'main/about.html', {'title': 'О сайте'})


class ShowItem(DataMixin, DetailView):
    template_name = 'main/item.html'
    slug_url_kwarg = 'item_slug'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=context['item'].name)

    def get_object(self, queryset=None):
        return get_object_or_404(Items.actual, slug=self.kwargs[self.slug_url_kwarg])


def show_menu(request, mtplace_slug):
    marketplace = get_object_or_404(Marketplace, slug=mtplace_slug)
    items_mtplace = Items.actual.filter(mtplace_id=marketplace.pk).select_related('mtplace')

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

class AddItem(DataMixin, CreateView):
    form_class = AddItemForm
    template_name = 'main/add_item.html'
    title = 'Добавление товара с маркетплейса'

class UpdateItem(DataMixin, UpdateView):
    model = Items
    fields = ['id_item', 'name', 'content', 'brand', 'mtplace', 'tags']
    template_name = 'main/add_item.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=f'Редактирование товара "{context['items'].name}"')


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
