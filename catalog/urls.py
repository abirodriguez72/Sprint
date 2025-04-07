from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('recipes/', views.RecipeListView.as_view(), name='recipe_list'),
    path('recipes/<uuid:pk>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
    path('categories/<slug:slug>/', views.category_detail, name='category_detail'),
    path('users/<uuid:user_id>/', views.user_detail, name='user_detail'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('recipes/<uuid:recipe_id>/review/', views.create_review, name='create_review'),
    path('', views.recipe_list, name='recipe_list'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('recipes/<uuid:recipe_id>/note/', views.create_recipe_note, name='create_recipe_note'),
]
