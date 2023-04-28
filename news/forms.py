# from django.forms import ModelForm, BooleanField # Импортируем true-false поле
from django.forms import ModelForm, BooleanField
from .models import Post

# Создаём модельную форму
class PostForm(ModelForm):
    check_box = BooleanField(label='Ало, Галочка!')  # добавляем галочку или же true-false поле
    class Meta:
        model = Post
        fields = ['title', 'text', 'author', 'category', 'check_box']  # не забываем включить галочку в поля, иначе она не будет показываться на странице!
        # fields = ['title', 'text', 'author', 'postCategory', 'check_box']  # не забываем включить галочку в поля, иначе она не будет показываться на странице!

