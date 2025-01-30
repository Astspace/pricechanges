nav = [
    {'title': "Добавить товар", 'url_name': 'add_item'},
    {'title': "Обратная связь", 'url_name': 'contact'},
]


def get_nav_context(request):
    return {'nav': nav}