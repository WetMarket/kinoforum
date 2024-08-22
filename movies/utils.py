menu = [{'title': "О сайте", 'url_name': 'about'},
        {'title': "Оставить отзыв", 'url_name': 'reviews'},
        {'title': "Обратная связь", 'url_name': 'contact'},
        {'title': "Добавление статьи", 'url_name': 'addpage'},
        {'title': "Войти", 'url_name': 'login'}]


class DataMixin:
    title_page = None
    paginate_by = 8
    extra_context = {}

    def __init__(self):
        if self.title_page:
            self.extra_context['title'] = self.title_page
        if 'menu' not in self.extra_context:
            self.extra_context['menu'] = menu

    def get_mixin_context(self, context, **kwargs):
        if self.title_page:
            context['title'] = self.title_page

        context['menu'] = menu
        context.update(kwargs)
        return context
