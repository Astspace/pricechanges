from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from .forms import AddItemForm
from .models import Items, Marketplace
from .utils import DataMixin
from main.services.processors import preparation_data_for_create_item, get_item_price_change


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


class ShowItem(DataMixin, DetailView):
    template_name = 'main/item.html'
    slug_url_kwarg = 'item_slug'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=context['item'].name)

    def get_object(self, queryset=None):
        return get_object_or_404(Items.actual, slug=self.kwargs[self.slug_url_kwarg])


class ShowMenu(DataMixin, ListView):
    template_name = 'main/index.html'
    context_object_name = 'data_item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mpl = Marketplace.objects.get(slug=self.kwargs['mtplace_slug'])
        return self.get_mixin_context(context, menu_selected=mpl.pk, title=f'Просмотр товаров с {mpl.name}')

    def get_queryset(self):
        return Items.actual.filter(mtplace__slug=self.kwargs['mtplace_slug']).select_related('mtplace')


class ShowTagItems(DataMixin, ListView):
    template_name = 'main/index.html'
    context_object_name = 'data_item'
    title = 'Просмотр товаров по тегам'

    def get_queryset(self):
        return Items.actual.filter(tags__slug=self.kwargs['tag_slug']).select_related('mtplace')


class AddItem(LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddItemForm
    template_name = 'main/add_item.html'
    title = 'Добавление товара с маркетплейса'

    def form_valid(self, form):
        data_for_create_item = form.save(commit=False)
        data_for_create_item.owner = self.request.user
        data_for_create_item = preparation_data_for_create_item(data_for_create_item)
        data_for_create_item.save()
        return super().form_valid(form)


class UpdateItem(DataMixin, UpdateView):
    model = Items
    fields = ['id_item', 'name', 'brand', 'mtplace', 'tags']
    template_name = 'main/add_item.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=f'Редактирование товара "{context['items'].name}"')


def contact(request):
    return HttpResponse("Обратная связь")


def login(request):
    return HttpResponse("Авторизация")


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")
