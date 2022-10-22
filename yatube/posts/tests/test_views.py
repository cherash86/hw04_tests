from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username="Test_User",)

        cls.group = Group.objects.create(
            title="тест-группа",
            slug="test_group",
            description="тестирование",
        )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=Group.objects.get(slug='test_group'),
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        self.user = User.objects.get(username="Test_User")
        #  Создаем авторизованый клиент
        self.authorized_client = Client()
        #  Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/post_detail.html':
                reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
            'posts/profile.html':
                reverse('posts:profile', kwargs={'username': 'Test_User'}),
            'posts/group_list.html':
                reverse('posts:group_list', kwargs={'slug': 'test_group'}),
        }
        # Проверяем, что при обращении к name вызывается соответствующий шаблон
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_pages_uses_correct_template(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_post_index_page_show_correct_context(self):
        """В шаблон posts/index.html пепредан правильный контекст."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, self.post.text)

    def test_group_list_page_show_correct_context(self):
        """В шаблон posts/group_list.html передан правильный контекст."""
        slug = self.group.slug
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': slug})
        )
        self.assertEqual(response.context['group'].slug, self.group.slug)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username="Test_User",)

        cls.group = Group.objects.create(
            title="тест-группа",
            slug="test_group",
            description="тестирование",
        )

        #  Создаём 13 тестовых записей
        for i in range(13):
            cls.post = Post.objects.create(
                text=f'Тестовый пост {i}',
                author=cls.user,
                group=Group.objects.get(slug='test_group'),
            )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        self.user = User.objects.get(username="Test_User")
        # Создаем авторизованый клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        """По 10 постов на первой странице у index, group_list и profile"""
        templates = [
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': 'Test_User'}),
            reverse('posts:group_list', kwargs={'slug': 'test_group'}),
        ]
        for template in templates:
            with self.subTest(template=template):
                response = self.guest_client.get(template)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """По 3 поста на второй странице index, group_list и profile"""
        templates = [
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': 'Test_User'}),
            reverse('posts:group_list', kwargs={'slug': 'test_group'}),
        ]
        for template in templates:
            with self.subTest(template=template):
                response = self.guest_client.get(template + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
