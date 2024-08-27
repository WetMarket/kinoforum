from django import template

register = template.Library()


@register.filter(name='ru_pluralize')
def ru_pluralize(value, endings="пользователь,пользователя,пользователей"):
    args = endings.split(',')
    try:
        value = int(value)
        if value % 10 == 1 and value % 100 != 11:
            return args[0]
        elif 2 <= value % 10 <= 4 and (value % 100 < 10 or value % 100 >= 20):
            return args[1]
        else:
            return args[2]
    except ValueError:
        return ''
