from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Test_User')
        cls.group = Group.objects.create(
            title='тест-группа',
            slug='test_group',
            description='Тестирование'
        )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group
        )
        # Создаём форму для проверки атрибутов
        cls.form = PostForm()

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        self.user = User.objects.get(username="Test_User")
        #  Создаем авторизованый клиент
        self.authorized_client = Client()
        #  Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """При отправке валидной формы создаётся новый пост"""
        # Подсчитаем количество записей
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.id,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse('posts:profile', kwargs={'username': self.user})
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с заданным текстом
        self.assertTrue(Post.objects.filter(text='Тестовый пост').exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_edit_post(self):
        """Валидная форма изменяет запись в Posts."""
        new_group = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug2',
            description='Тестовое описание 2',
        )

        form_data = {
            'text': 'Отредактированный в форме текст',
            'group': new_group.pk,
        }
        response = self.authorized_client_author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        post_edit = Post.objects.get(id=self.post.pk)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post_edit.text, form_data['text'])
        self.assertEqual(post_edit.group.pk, form_data['group'])
        self.assertEqual(
            post_edit.author,
            self.post.author,
            'ошибка с автором поста при редактировании'
        )
