from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User
from .utils import get_page_context


NUM = 10


def index(request):
    post_list = Post.objects.select_related('group')
    page_obj = get_page_context(request, post_list, NUM)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = get_page_context(request, post_list, NUM)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page_obj = get_page_context(request, post_list, NUM)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post_info = get_object_or_404(Post, pk=post_id)
    number_of_posts = post_info.author.posts.count()
    context = {
        'post_info': post_info,
        'number_of_posts': number_of_posts,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author_id = request.user.id
            instance.save()
            user_name = request.user.username
            return redirect('posts:profile', user_name)
        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, instance=post)
    #  Если редактирует не автор
    if request.user != post.author:
        # Перенаправляем на страницу просмотра поста
        return redirect('posts:post_detail', post.id)
    elif request.method == 'POST':
        if form.is_valid():
            form.save()
        return redirect('posts:post_detail', post.id)

    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    return render(request, 'posts/create_post.html', context)
