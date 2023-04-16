from django.urls import path
from .views import PostsList, PostsDetail, PostsSearch, PostsAdd, PostsEdit, PostsDelete #ProtectedView     импортируем наше представление

urlpatterns = [                             # path — означает путь. В данном случае путь ко всем товарам у нас останется пустым, позже станет ясно почему
    path('', PostsList.as_view()),          # т.к. сам по себе это класс, то нам надо представить этот класс в виде view. Для этого вызываем метод as_view
    path('<int:pk>/', PostsDetail.as_view(), name='new'),       # pk — это первичный ключ товара, который будет выводиться у нас в шаблон
    path('search/', PostsSearch.as_view(), name='search'),
    path('add/', PostsAdd.as_view(), name='add'),
    path('edit/<int:pk>/', PostsEdit.as_view(), name='edit'),
    path('delete/<int:pk>/', PostsDelete.as_view(), name='delete'),
    #path('login/', ProtectedView.as_view(), name='login'),
    #path('accounts/', include('allauth.urls')),
]