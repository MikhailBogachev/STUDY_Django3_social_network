from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()


class StaticViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='User'
        )
        cls.group = Group.objects.create(
            title='Название группы',
            slug='test-slug',
            description='Описание группы'
        )
        Group.objects.create(
            title='Название группы 2',
            slug='test-slug-2',
            description='Описание группы 2'
        )
        Post.objects.create(
            text='Текст поста',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        # Создаем авторизованый клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(StaticViewTests.user)

    def test_create_post_form(self):
        """Проверяем создание поста при отправке валидной формы"""
        count_post = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': 1
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, '/profile/User/')
        self.assertEqual(Post.objects.count(), count_post + 1)

    def test_edit_post_form(self):
        """Проверяем редактирование поста при отправке валидной формы"""
        form_data = {
            'text': 'Измененный Тестовый текст',
            'group': 2
        }
        post_text = Post.objects.get(pk=1).text
        post_group = Post.objects.get(pk=1).group.id
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': 1}),
            data=form_data,
            follow=True
        )
        edit_post_text = Post.objects.get(pk=1).text
        edit_post_group = Post.objects.get(pk=1).group.id

        self.assertNotEqual(post_text, edit_post_text)
        self.assertNotEqual(post_group, edit_post_group)
        self.assertEqual(edit_post_text, 'Измененный Тестовый текст')
        self.assertEqual(edit_post_group, 2)
        self.assertEqual(Post.objects.filter(group=1).count(), 0)
        self.assertEqual(Post.objects.filter(group=2).count(), 1)
