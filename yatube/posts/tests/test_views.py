from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms

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
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(StaticViewTests.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('posts:index'): (
                'posts/index.html'
            ),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={'username': 'User'}): (
                'posts/profile.html'
            ),
            reverse('posts:post_detail', kwargs={'post_id': 1}): (
                'posts/post_detail.html'
            ),
            reverse('posts:post_create'): (
                'posts/create_post.html'
            ),
            reverse('posts:post_edit', kwargs={'post_id': 1}): (
                'posts/create_post.html'
            ),
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def post_context_is_correct(self, obj):
        task_text = obj.text
        task_author = obj.author.username
        task_group = obj.group.title
        self.assertEqual(task_text, 'Текст поста')
        self.assertEqual(task_author, 'User')
        self.assertEqual(task_group, 'Название группы')

    def test_index_page_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.post_context_is_correct(first_object)

    def test_group_page_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        first_object = response.context['page_obj'][0]
        group_object = response.context['group']
        task_group_title = group_object.title
        task_group_slug = group_object.slug
        task_group_description = group_object.description

        self.post_context_is_correct(first_object)
        self.assertEqual(task_group_title, 'Название группы')
        self.assertEqual(task_group_slug, 'test-slug')
        self.assertEqual(task_group_description, 'Описание группы')

    def test_profile_page_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'User'})
        )
        first_object = response.context['page_obj'][0]
        author_object = response.context['author']
        post_count_object = response.context['post_count']
        task_author_username = author_object.username
        task_post_count = post_count_object

        self.post_context_is_correct(first_object)
        self.assertEqual(task_author_username, 'User')
        self.assertEqual(task_post_count, 1)

    def test_post_detail_page_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1})
        )
        first_object = response.context['post']
        post_count_object = response.context['post_count']
        task_post_count = post_count_object

        self.post_context_is_correct(first_object)
        self.assertEqual(task_post_count, 1)

    def test_post_create_page_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        first_group = response.context['group'][0]
        task_group = first_group.title

        self.assertEqual(task_group, 'Название группы')

    def test_post_edit_page_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 1})
        )

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        first_group = response.context['group'][0]
        post_obj = response.context['post']
        key_is_edit = response.context['is_edit']
        task_group = first_group.title
        task_post_text = post_obj.text
        task_post_author = post_obj.author.username
        task_is_edit = key_is_edit

        self.assertEqual(task_group, 'Название группы')
        self.assertEqual(task_post_text, 'Текст поста')
        self.assertEqual(task_post_author, 'User')
        self.assertEqual(task_is_edit, True)


class PaginatorViewTests(TestCase):
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
        for num_post in range(1, 16):
            Post.objects.create(
                text=f'Текст поста {num_post}',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewTests.user)

    def test_index_first_page(self):
        """Шаблон index выводит нужное кол-во постов на первую страницу"""
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page(self):
        """Шаблон index выводит нужное кол-во постов на вторую страницу"""
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_group_post_first_page(self):
        """Шаблон group_post выводит нужное кол-во постов на первую страницу"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_post_second_page(self):
        """Шаблон group_post выводит нужное кол-во постов на вторую страницу"""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            )
            + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_profile_first_page(self):
        """Шаблон profile выводит нужное кол-во постов на первую страницу"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'User'})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page(self):
        """Шаблон profile выводит нужное кол-во постов на вторую страницу"""
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={'username': 'User'}
            )
            + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 5)
