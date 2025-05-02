from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.views.static import serve

from catalog import views as catalog_views
from catalog.views import CategoryListView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Catalog App
    path('', catalog_views.home, name='home'),
    path('recipes/', catalog_views.RecipeListView.as_view(), name='recipe_list'),
    path('recipes/<uuid:pk>/', catalog_views.RecipeDetailView.as_view(), name='recipe_detail'),
    path('recipes/<uuid:recipe_id>/review/', catalog_views.create_review, name='create_review'),
    path('recipes/<uuid:recipe_id>/note/', catalog_views.create_recipe_note, name='create_recipe_note'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', catalog_views.category_detail, name='category_detail'),
    path('users/<int:user_id>/', catalog_views.user_detail, name='user_detail'),

    # Authentication
    path('signup/', catalog_views.signup_view, name='signup'),
    path('login/', catalog_views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),

    # Forum App
    path('forum/', include('forum.urls')),
]

# Serve media & static in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Fallback serving via Django (not recommended for production)
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]
