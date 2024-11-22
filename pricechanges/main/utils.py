class DataMixin:
    title = None
    extra_context = {}
    menu_selected = None

    def __init__(self):
        if self.title:
            self.extra_context['title'] = self.title

        if self.menu_selected is not None:
            self.extra_context['menu_selected'] = self.menu_selected

    def get_mixin_context(self, context, **kwargs):
        context['cat_selected'] = None
        context.update(kwargs)
        return context