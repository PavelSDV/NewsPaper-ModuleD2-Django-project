from django.urls import path
from .views import PostsList, PostsDetail, PostsSearch, PostsAdd, PostsEdit, PostsDelete, upgrade_me, \
    PostCategoryView, subscribe_to_category, unsubscribe_to_category
# from django.views.decorators.cache import cache_page    # caching  commit37


urlpatterns = [                             # path — означает путь. В данном случае путь ко всем товарам у нас останется пустым, позже станет ясно почему
    path('', PostsList.as_view()),          # т.к. сам по себе это класс, то нам надо представить этот класс в виде view. Для этого вызываем метод as_view
    # path('', cache_page(60*1)(PostsList.as_view())),          # caching  commit37
    # path('<int:pk>/', cache_page(60*5)(PostsDetail.as_view()), name='new'),       # pk — это первичный ключ товара, который будет выводиться у нас в шаблон
    path('<int:pk>/', PostsDetail.as_view(), name='new'),       # pk — это первичный ключ товара, который будет выводиться у нас в шаблон
    path('search/', PostsSearch.as_view(), name='search'),
    path('add/', PostsAdd.as_view(), name='add'),
    path('edit/<int:pk>/', PostsEdit.as_view(), name='edit'),
    path('delete/<int:pk>/', PostsDelete.as_view(), name='delete'),
    path('upgrade/', upgrade_me, name = 'upgrade'),
    path('category/<int:pk>/', PostCategoryView.as_view(), name='category'),
    path('subscribe/<int:pk>/', subscribe_to_category, name='subscribe'),
    path('unsubscribe/<int:pk>/', unsubscribe_to_category, name='unsubscribe'),
]