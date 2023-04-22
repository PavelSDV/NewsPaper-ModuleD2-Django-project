from django.shortcuts import render, reverse, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView #, TemplateView   # импортируем класс, который говорит нам о том, что в этом представлении мы будем выводить список объектов из БД
from django.core.paginator import Paginator # импортируем класс, позволяющий удобно осуществлять постраничный вывод

from .models import Post, Category
from .filters import PostFilter # импортируем недавно написанный фильтр
from .forms import PostForm # импортируем нашу форму

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group

from django.contrib.auth.decorators import login_required

from django.views import View
from django.core.mail import send_mail, EmailMultiAlternatives       # импортируем класс для создание объекта письма с html
from datetime import datetime
from django.urls import resolve
from django.template.loader import render_to_string

# Create your views here.
class PostsList(ListView):
    model = Post                            # указываем модель, объекты которой мы будем выводить
    template_name = 'news.html'             # указываем имя шаблона, в котором будет лежать HTML, в нём будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    context_object_name = 'news'            # это имя списка, в котором будут лежать все объекты, его надо указать, чтобы обратиться к самому списку объектов через HTML-шаблон
    paginate_by = 10                        # поставим постраничный вывод в 10 элементов
    ordering = ['-dataCreation']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        return context

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

class PostsAdd(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Post  # указываем модель, объекты которой мы будем выводить
    template_name = 'add.html'  # указываем имя шаблона, в котором будет лежать HTML, в нём будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    form_class = PostForm  # добавляем форм класс, чтобы получать доступ к форме через метод POST
    success_url = '/news/'
    permission_required = ('news.add_post')

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
class PostsEdit(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post
    template_name = 'edit.html'
    form_class = PostForm
    success_url = '/news/'
    permission_required = ('news.change_post')

    # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте который мы собираемся редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        return context

# дженерик для удаления товара
class PostsDelete(LoginRequiredMixin, DeleteView):
    template_name = 'delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'

# Всех новых зарегистрированных сразу в группу common
class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)
        return user

@login_required
def upgrade_me(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
    return redirect('/')

# class PostsCategoryView(ListView):
#     model = Post                              # указываем модель, объекты которой мы будем выводить
#     template_name = 'category.html'           # указываем имя шаблона, в котором будет лежать HTML, в нём будут все инструкции о том, как именно пользователю должны вывестись наши объекты
#     context_object_name = 'posts'             # это имя списка, в котором будут лежать все объекты, его надо указать, чтобы обратиться к самому списку объектов через HTML-шаблон
#     paginate_by = 10                          # поставим постраничный вывод в 10 элементов
#     ordering = ['-created_at']
#
#     def get_queryset(self):
#         self.id = resolve(self.request.path_info).kwargs['pk']
#         с = Category.objects.get(id=self.id)
#         queryset = Post.objects.filter(category=c)
#         return queryset
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         user = self.request.user
#         category = Category.objects.get(id=self.id)
#         subscribed = category.subscribers.filter(email=user.email)
#         return context
#
# def subscribe_to_category(request, pk):
#     user = request.user
#     category = Category.objects.get(id=pk)
#     if not category.subscribers.filter(id=user.id).exists():
#         category.subscribers.add(user)
#         email = user.email
#         html = render_to_string(
#             'subscribe.html',
#             {
#                 'category': category,
#                 'user': user,
#             }
#         )
#         msg = EmailMultiAlternatives(
#             subject=f'{category} subscription',
#             body='',
#             from_email='newspaperss@yandex.ru',
#             to=[email,],
#         )
#
#         msg.attach_alternative(html, ('text/html',))
#
#         try:
#             msg.send()
#         except Exception as e:
#             print(e)
#         return redirect('/')
#     return redirect(request.META.get('HTTP_REFERER'))



# def unsubscribe_to_category(request, pk):
#     user = request.user
#     category = Category.objects.get(id=pk)