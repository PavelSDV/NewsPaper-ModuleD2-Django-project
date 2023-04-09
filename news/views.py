from django.shortcuts import render
from django.views.generic import ListView, DetailView   # импортируем класс, который говорит нам о том, что в этом представлении мы будем выводить список объектов из БД
from django.core.paginator import Paginator # импортируем класс, позволяющий удобно осуществлять постраничный вывод

from .models import Post
from .filters import PostFilter # импортируем недавно написанный фильтр

# Create your views here.
class PostsList(ListView):
    model = Post                            # указываем модель, объекты которой мы будем выводить
    template_name = 'news.html'             # указываем имя шаблона, в котором будет лежать HTML, в нём будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    context_object_name = 'news'            # это имя списка, в котором будут лежать все объекты, его надо указать, чтобы обратиться к самому списку объектов через HTML-шаблон
    ordering = ['-dataCreation']
    paginate_by = 5  # поставим постраничный вывод в один элемент

# создаём представление, в котором будут детали конкретного отдельного товара
class PostsDetail(DetailView):
    model = Post                            # модель всё та же, но мы хотим получать детали конкретно отдельного товара
    template_name = 'new.html'              # название шаблона будет product.html
    context_object_name = 'new'             # название объекта


class PostsSearch(ListView):
    model = Post  # указываем модель, объекты которой мы будем выводить
    template_name = 'search.html'  # указываем имя шаблона, в котором будет лежать HTML, в нём будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    #context_object_name = 'search'  # это имя списка, в котором будут лежать все объекты
    ordering = ['-dataCreation']

    def get_context_data(self, **kwargs):  # забираем отфильтрованные объекты переопределяя метод get_context_data у наследуемого класса (привет, полиморфизм, мы скучали!!!)
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())  # вписываем наш фильтр в контекст
        return context
