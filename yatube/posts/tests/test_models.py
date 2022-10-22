from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='тест-группа',
            slug='test_group',
            description='Тестирование',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        group = PostModelTest.group
        expected_object_name_group = group.title
        self.assertEqual(expected_object_name_group, str(group))

        post = PostModelTest.post
        expected_object_name_post = post.text[:15]
        self.assertEqual(expected_object_name_post, str(post))
