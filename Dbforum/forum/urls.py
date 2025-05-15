from django.urls import path
from . import views

urlpatterns = [
    path('', views.forum_home, name='forum_home'),
    path('create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('menu/', views.menu_page, name='menu_page'),  # new
    path('shop/', views.shop_page, name='shop_page'),  # new
]
