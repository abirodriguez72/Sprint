from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Reply

def forum_home(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'forum/home.html', {'posts': posts})

def create_post(request):
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        image = request.FILES.get('image')  # <-- Add this
        Post.objects.create(title=title, content=content, image=image)
        return redirect('forum_home')
    return render(request, 'forum/create_post.html')


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        content = request.POST['content']
        Reply.objects.create(post=post, content=content)
        return redirect('post_detail', post_id=post.id)
    return render(request, 'forum/post_detail.html', {'post': post})

def menu_page(request):
    return render(request, 'forum/menu.html')

def shop_page(request):
    return render(request, 'forum/shop.html')
