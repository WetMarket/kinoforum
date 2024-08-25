from movies.utils import menu


def get_movie_context(request):
    if not request.user.has_perm('movies.add_movie'):
        filtered_menu = [item for item in menu if item['url_name'] != 'addpage']
    else:
        filtered_menu = menu

    return {'mainmenu': filtered_menu}
