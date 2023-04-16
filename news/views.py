from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView   # импортируем класс, который говорит нам о том, что в этом представлении мы будем выводить список объектов из БД
from django.core.paginator import Paginator # импортируем класс, позволяющий удобно осуществлять постраничный вывод
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Post
from .filters import PostFilter # импортируем недавно написанный фильтр
from .forms import PostForm # импортируем нашу форму

from django.contrib.auth.models import User
#from .models import BaseRegisterForm

# Create your views here.
class PostsList(ListView):
    model = Post                            # указываем модель, объекты которой мы будем выводить
    template_name = 'news.html'             # указываем имя шаблона, в котором будет лежать HTML, в нём будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    context_object_name = 'news'            # это имя списка, в котором будут лежать все объекты, его надо указать, чтобы обратиться к самому списку объектов через HTML-шаблон
    paginate_by = 10                        # поставим постраничный вывод в 10 элементов
    ordering = ['-dataCreation']

# создаём представление, в котором будут детали конкретного отдельного товара
class PostsDetail(DetailView):
    model = Post                            # модель всё та же, но мы хотим получать детали конкретно отдельного товара
    template_name = 'new.html'              # название шаблона будет product.html
    context_object_name = 'new'             # название объекта

class PostsSearch(ListView):
    model = Post  # указываем модель, объекты которой мы будем выводить
    template_name = 'search.html'  # указываем имя шаблона, в котором будет лежать HTML, в нём будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    ordering = ['-dataCreation']

    def get_context_data(self, **kwargs):  # забираем отфильтрованные объекты переопределяя метод get_context_data у наследуемого класса (привет, полиморфизм, мы скучали!!!)
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())  # вписываем наш фильтр в контекст
        context['form'] = PostForm()
        return context

class PostsAdd(CreateView):
    model = Post  # указываем модель, объекты которой мы будем выводить
    template_name = 'add.html'  # указываем имя шаблона, в котором будет лежать HTML, в нём будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    form_class = PostForm  # добавляем форм класс, чтобы получать доступ к форме через метод POST
    success_url = '/news/'

    def get_context_data(self, **kwargs):  # забираем отфильтрованные объекты переопределяя метод get_context_data у наследуемого класса (привет, полиморфизм, мы скучали!!!)
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)  # создаём новую форму, забиваем в неё данные из POST-запроса

        if form.is_valid():  # если пользователь ввёл всё правильно и нигде не накосячил, то сохраняем новый товар
            form.save()
            return redirect(self.success_url)

        return super().get(request, *args, **kwargs)

# дженерик для редактирования объекта
class PostsEdit(UpdateView):
    template_name = 'edit.html'
    form_class = PostForm
    success_url = '/news/'

    # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте который мы собираемся редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)

# дженерик для удаления товара
class PostsDelete(DeleteView):
    template_name = 'delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'

# class ProtectedView(LoginRequiredMixin, TemplateView):
#     template_name = 'edit.html'

# class BaseRegisterView(CreateView):
#     model = User
#     template_name = 'signup.html'
#     form_class = BaseRegisterForm
#     success_url = '/'
#
# class LoginView(CreateView):
#     model = User
#     template_name = 'login.html'
#     #form_class = BaseRegisterForm
#     success_url = '/'
#
# class LogoutView(CreateView):
#     model = User
#     template_name = 'logout.html'
#     #form_class = BaseRegisterForm
#     success_url = '/'