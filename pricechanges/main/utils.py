class DataMixin:
    paginate_by = 3
    title = None
    extra_context = {}
    menu_selected = None

    def __init__(self):
        if self.title:
            self.extra_context['title'] = self.title

        self.extra_context['menu_selected'] = self.menu_selected

    def get_mixin_context(self, context, **kwargs):
        context['menu_selected'] = None
        context.update(kwargs)
        return context