from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from loguru import logger
from .forms import AddItemForm
from .models import Items, Marketplace
from .services.processors import get_image_graph_price_changes, get_image_graph_actual_price
from .utils import DataMixin
from main.services import processors


class HomeItems(DataMixin, ListView):
    template_name = 'main/index.html'
    context_object_name = 'data_item'
    title = 'Главная страница'
    menu_selected = 0

    def get_queryset(self):
        return Items.actual.filter(owner_id=self.request.user.id).select_related('mtplace')


class AddItemError(DataMixin, TemplateView):
    template_name = 'main/add_item_error.html'
    title = 'О сайте'


class ShowItem(DataMixin, DetailView):
    template_name = 'main/item.html'
    slug_url_kwarg = 'item_slug'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item_history = processors.get_list_item_history(item_relations=context['item'].id)
        if isinstance(item_history, QuerySet):
            data_history = {'type': 'queryset', 'data': item_history}
        else:
            data_history = {'type': 'error', 'data': item_history}
        return self.get_mixin_context(context, title=context['item'].name, history=data_history,
                                      graph=get_image_graph_price_changes(item_history),
                                      graph_actual=get_image_graph_actual_price(item_history))

    def get_object(self, queryset=None):
        return get_object_or_404(Items.actual, slug=self.kwargs[self.slug_url_kwarg],
                                 owner_id=self.request.user.id)


class ShowMenu(DataMixin, ListView):
    template_name = 'main/index.html'
    context_object_name = 'data_item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mpl = Marketplace.objects.get(slug=self.kwargs['mtplace_slug'])
        return self.get_mixin_context(context, menu_selected=mpl.pk,
                                      title=f'Просмотр товаров с {mpl.name}')

    def get_queryset(self):
        return Items.actual.filter(mtplace__slug=self.kwargs['mtplace_slug'],
                                   owner_id=self.request.user.id).select_related('mtplace')


class ShowTagItems(DataMixin, ListView):
    template_name = 'main/index.html'
    context_object_name = 'data_item'
    title = 'Просмотр товаров по тегам'

    def get_queryset(self):
        return Items.actual.filter(tags__slug=self.kwargs['tag_slug'],
                                   owner_id=self.request.user.id).select_related('mtplace')


class AddItem(LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddItemForm
    template_name = 'main/add_item.html'
    title = 'Добавление товара с маркетплейса'

    def form_valid(self, form):
        data_for_create_item = form.save(commit=False)
        data_for_create_item.owner = self.request.user
        data_for_create_item = processors.preparation_data_for_create_item(data_for_create_item)
        if isinstance(data_for_create_item, str):
            return render(self.request, 'main/add_item_error.html', {'error_msg': data_for_create_item})
        try:
            data_for_create_item.save()
        except Exception:
            err_msg = 'Непредвиденная ошибка в процессе добавления нового товара. Обратитесь к разрабочтику.'
            logger.exception(err_msg)
            return render(self.request, 'maim/add_item_error.html', {'error_msg': err_msg})
        processors.history_for_created_item(created_item=data_for_create_item)
        processors.send_add_item_message(created_item=data_for_create_item)
        return super().form_valid(form)


class UpdateItem(DataMixin, UpdateView):
    model = Items
    fields = ['name_for_user', 'brand', 'tags']
    template_name = 'main/add_item.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=f'Редактирование товара "{context['items'].name}"')


def contact(request):
    return HttpResponse("Обратная связь")


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")
