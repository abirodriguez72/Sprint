from django.contrib import admin
from .models import Category, User, UserType, Recipe, Review

admin.site.register(Category)
admin.site.register(UserType)
admin.site.register(Recipe)
admin.site.register(Review)

