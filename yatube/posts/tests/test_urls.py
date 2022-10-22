from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username="Test_User",)

        cls.group = Group.objects.create(
            title="тест-группа",
            slug="test_group",
            description="Тестирование",
        )

        cls.post = Post.objects.create(
            id='1',
            text='Тестовый пост',
            author=User.objects.get(username="Test_User"),
            group=Group.objects.get(title="тест-группа"),
        )

        cls.post_url = f'/posts/{cls.post.id}/'
        cls.post_edit_url = f'/posts/{cls.post.id}/edit/'
        # Кортеж общедоступных страниц
        cls.public_urls = (
            ('/', 'index.html'),
            (f'/group/{cls.group.slug}/', 'group.html'),
            (f'/profile/{cls.user.username}/', 'profile.html'),
            (cls.post_url, 'post.html'),
        )
        # Кортеж страниц, доступных для авторизованного пользователя
        cls.private_urls = (
            ('/create/', 'create_post.html'),
            (cls.post_edit_url, 'create_post.html')
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        self.user = User.objects.get(username="Test_User")
        # Создаем авторизованый клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    # Проверяем общедоступные страницы
    def test_public_pages(self):
        for url in self.public_urls:
            response = self.guest_client.get(url[0])
            self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем доступ для авторизованного пользователя
    def test_private_pages(self):
        for url in self.private_urls:
            response = self.authorized_client.get(url[0])
            self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем запрос к несуществующей страницe
    def test_task_list_url_redirect_anonymous(self):
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    # Проверка вызываемых HTML-шаблонов для каждого адреса
    def test_post_urls_uses_correct_template(self):
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test_group/': 'posts/group_list.html',
            '/profile/Test_User/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
