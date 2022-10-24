from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()
Author = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Test_User')
        cls.author = Author.objects.create(username='Test_User2')
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
        #  Создаем авторизованый клиент
        self.authorized_client = Client()
        #  Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        self.noauthorized_client = Client()
        self.noauthorized_client.force_login(self.author)

    def test_create_post(self):
        """При отправке валидной формы создаётся новый пост"""
        # Подсчитаем количество записей
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый постовой',
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
        self.assertTrue(Post.objects.filter(text='Тестовый постовой',
                        group=self.group.id).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_client_post_create(self):
        """"Неавторизованный клиент не может создавать посты."""
        form_data = {
            'text': 'Пост от неавторизованного клиента',
            'group': self.group.id
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertFalse(Post.objects.filter(
            text='Пост от неавторизованного клиента').exists())

    def test_post_edit(self):
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
        response = self.authorized_client.post(
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

    def test_not_author_can_edit_post(self):
        """Проверка прав редактирования"""
        old_post = self.post
        self.group2 = Group.objects.create(title='Тестовая группа2',
                                           slug='test-group',
                                           description='Описание')
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group2.id}
        response = self.noauthorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.post.refresh_from_db()
        # error_name1 = 'Пользователь не может изменить содержание поста'
        self.assertNotEqual(old_post.text, form_data['text'])
        # error_name2 = 'Пользователь не может изменить группу поста'
        self.assertNotEqual(self.post.group.id, form_data['group'])
