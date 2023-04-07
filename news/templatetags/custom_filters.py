from django import template

register = template.Library()       # если мы не зарегестрируем наши фильтры, то django никогда не узнает где именно их искать и фильтры потеряются :(

badwordsList = ['badword1', 'badword2', 'badword3']

@register.filter(name='censor')     # регистрируем наш фильтр под именем censor, чтоб django понимал, что это именно фильтр, а не простая функция
def censor(value):                   # первый аргумент здесь — это то значение, к которому надо применить фильтр
    for word in badwordsList:
        value = value.replace(word, '***')
    return value


