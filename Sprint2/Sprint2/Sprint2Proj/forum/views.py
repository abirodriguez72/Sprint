from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Reply, Follow
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Post
from .forms import PostForm


@login_required
def forum_home(request):
    posts = Post.objects.all()
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('forum_home')
    return render(request, 'forum/forum_home.html', {'posts': posts, 'form': form})


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        Reply.objects.create(
            post=post,
            # post.user = request.user  ← comment this out or delete
            content=request.POST['reply']
        )
        return redirect('post_detail', post_id=post_id)
    return render(request, 'forum/post_detail.html', {'post': post})

@login_required
def follow_user(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    Follow.objects.get_or_create(follower=request.user, following=target_user)
    return redirect('forum_home')


# Create your views here.
def forum_home(request):
    return render(request, 'forum/home.html')