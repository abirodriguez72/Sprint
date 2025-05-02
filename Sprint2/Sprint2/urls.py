from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('forum/', permanent=False)),  # 👈 This redirects root
    path('admin/', admin.site.urls),
    path('forum/', include('forum.urls')),
]
