from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # All root-level URLs go to your catalog app
    path('', include('catalog.urls')),
]
