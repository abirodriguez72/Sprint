from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import Group, User
from django.conf import settings
import uuid

CATEGORY_TYPE_CHOICES = [
    ('main', 'Main Category'),
    ('sub', 'Subcategory'),
]

RATING_CHOICES = [
    (1, '1 - Very Poor'),
    (2, '2 - Poor'),
    (3, '3 - Average'),
    (4, '4 - Good'),
    (5, '5 - Excellent'),
]


class Category(models.Model):
    """Model representing a recipe category or subcategory."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text='Enter a category of baked good (e.g., Breads, Cakes)'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories',
        help_text='Select a parent category if this is a subcategory'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        help_text='Auto-generated from name if left blank'
    )
    icon = models.ImageField(
        upload_to='category_icons/',
        null=True,
        blank=True,
        help_text='Optional icon for this category'
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        help_text='Optional hex color code (e.g. #ffcc00)'
    )
    category_type = models.CharField(
        max_length=10,
        choices=CATEGORY_TYPE_CHOICES,
        default='main',
        help_text='Main category or subcategory'
    )

    class Meta:
        ordering = ['parent__name', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f'{self.parent.name} > {self.name}' if self.parent else self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class UserType(models.Model):
    """Model representing different types of users (e.g., Admin, Pro, Baker)."""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    group = models.ForeignKey('auth.Group', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class Profile(models.Model):
    """Profile model to extend the default Django User model."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    real_name = models.CharField(max_length=100, help_text='Enter your name')
    bio = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    user_type = models.ForeignKey(UserType, on_delete=models.SET_NULL, null=True, blank=True)

    def get_absolute_url(self):
        # Adjust the URL pattern as needed
        return reverse('user_detail', args=[str(self.user.id)])

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Recipe(models.Model):
    """Model representing a recipe (but not a specific user's review of a recipe)."""
    recipe_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    # Foreign Key used because a recipe can only be written by one user, but users can have multiple recipes
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, null=True)
    ingredients = models.TextField(
        max_length=1000,
        help_text='Enter the ingredients in quantity + ingredient format, e.g., "4 tbsp sugar".'
    )
    instructions = models.TextField(
        'Instructions',
        blank=False,
        null=False,
        help_text='Enter the recipe instructions.'
    )
    notes = models.TextField(blank=True, null=True)
    # ManyToManyField used because a category can contain many recipes.
    category = models.ManyToManyField(Category, help_text='Select a category for this recipe')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    photo = models.ImageField(upload_to='recipe_pics/', blank=True, null=True)
    rating = models.FloatField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this recipe."""
        return reverse('recipe_detail', args=[str(self.recipe_id)])

    @property
    def average_rating(self):
        reviews = self.review_set.all()
        if reviews.exists():
            return round(sum([r.rating for r in reviews]) / reviews.count(), 1)
        return None


class Review(models.Model):
    """Model representing a user's review of a recipe."""
    review_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text='The recipe being reviewed.'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text='The user who wrote the review.'
    )

    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        default=3,
        help_text='Rating given by the user (1 to 5).'
    )
    comment = models.TextField(
        blank=True,
        null=True,
        help_text='Optional comment provided by the user.'
    )
    created_at = models.DateTimeField(auto_now_add=True)

class RecipeNote(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.TextField()
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.user_name} - Note on {self.recipe.title}"
