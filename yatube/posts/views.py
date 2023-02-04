from django.shortcuts import render, get_object_or_404

from .models import Post, Group


def index(request):
    """Вью для отображения главной страницы с публикациями"""
    template: str = 'posts/index.html'
    posts = Post.objects.order_by('-pub_date')[:10]
    context: dict = {
        'posts': posts,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Вью для отображения страниц с постами конкретной группы"""
    template: str = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    context: dict = {
        'group': group,
        'posts': posts,
    }
    return render(request, template, context)
