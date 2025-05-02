from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic, View
from django.db.models import Q
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from .models import Recipe, Category, User, Review, RecipeNote
from .forms import (CustomUserCreationForm, ProfileForm, UserLoginForm,
                    RecipeForm, ReviewForm, RecipeNoteForm)
from .decorators import group_required

# Home view: Displays recent recipes and top-level categories.
def home(request):
    recent_recipes = Recipe.objects.order_by('-created_at')[:6]
    top_categories = Category.objects.filter(parent=None)
    num_recipes = Recipe.objects.count()
    num_reviews = Review.objects.count()
    num_users = User.objects.count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    context = {
        'recent_recipes': recent_recipes,
        'categories': top_categories,
        'num_recipes': num_recipes,
        'num_reviews': num_reviews,
        'num_users': num_users,
        'num_visits': num_visits,
    }
    return render(request, 'index.html', context)

# Recipe List View
class RecipeListView(generic.ListView):
    model = Recipe
    template_name = 'recipes/recipe_list.html'
    context_object_name = 'recipes'
    paginate_by = 10  # Display 10 recipes per page

# Recipe Detail View (includes Reviews)
from .models import RecipeNote

class RecipeDetailView(generic.DetailView):
    model = Recipe
    template_name = 'recipes/recipe_details.html'
    context_object_name = 'recipe'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # existing context
        ctx['reviews']        = self.object.reviews.all()
        ctx['average_rating'] = self.object.average_rating
        ctx['notes']          = RecipeNote.objects.filter(recipe=self.object, is_public=True)

        # add the current user’s private note (if any)
        user = self.request.user
        if user.is_authenticated:
            ctx['user_note'] = RecipeNote.objects.filter(
                recipe=self.object,
                user=user,
                is_public=False
            ).first()
        else:
            ctx['user_note'] = None

        return ctx

def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, recipe_id=recipe_id)
    reviews = recipe.reviews.all()
    average = recipe.average_rating
    public_notes = RecipeNote.objects.filter(recipe=recipe, is_public=True)

    # load any private note by this user on this recipe
    user_note = None
    if request.user.is_authenticated:
        user_note = RecipeNote.objects.filter(
            recipe=recipe,
            user=request.user,
            is_public=False
        ).first()

    form = None
    existing_review = None
    if request.user.is_authenticated:
        existing_review = Review.objects.filter(recipe=recipe, user=request.user).first()
        if request.method == 'POST' and not existing_review:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.recipe = recipe
                review.user = request.user
                review.save()
                return redirect('recipe_detail', recipe_id=recipe.recipe_id)
        else:
            form = ReviewForm()

    return render(request, 'recipes/recipe_details.html', {
        'recipe': recipe,
        'reviews': reviews,
        'average_rating': average,
        'form': form,
        'existing_review': existing_review,
        'notes': public_notes,
        'user_note': user_note,
    })

# Category Detail View: Displays a category, its subcategories, and its recipes.
def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    recipes = Recipe.objects.filter(category=category)
    subcategories = category.subcategories.all()
    context = {
        'category': category,
        'recipes': recipes,
        'subcategories': subcategories,
    }
    return render(request, 'categories/category_details.html', context)

# Signup view: Creates a new user and profile.
def signup_view(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            # Optionally, log the user in here.
            return redirect('user_detail', user_id=user.id)
    else:
        user_form = CustomUserCreationForm()
        profile_form = ProfileForm()
    return render(request, 'users/signup.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

# Login view: Logs the user in.
def login_view(request):
    error = None
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)                  # ← log them in
                return redirect('user_detail', user_id=user.id)
            else:
                error = "Invalid username or password"
    else:
        form = UserLoginForm()

    return render(request, 'users/login.html', {'form': form, 'error': error})

# User Detail View: Displays a user profile and their recipes and reviews.
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    recipes = Recipe.objects.filter(user=user)
    reviews = Review.objects.filter(user=user)
    context = {
        'user': user,
        'recipes': recipes,
        'reviews': reviews,
    }
    return render(request, 'users/user_details.html', context)

# Creates Recipe view.
def create_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.user = request.user  # Assumes the user is logged in.
            recipe.save()
            form.save_m2m()
            return redirect(recipe.get_absolute_url())
    else:
        form = RecipeForm()
    return render(request, 'recipes/recipe_form.html', {'form': form})

# Creates Review view
def create_review(request, recipe_id):
    recipe = get_object_or_404(Recipe, recipe_id=recipe_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.recipe = recipe
            review.user = request.user
            review.save()
            return redirect(recipe.get_absolute_url())
    else:
        form = ReviewForm()
    return render(request, 'recipes/review_form.html', {'form': form, 'recipe': recipe})

# Creates Recipe note
@login_required
def create_recipe_note(request, recipe_id):
    recipe = get_object_or_404(Recipe, recipe_id=recipe_id)
    if request.method == 'POST':
        form = RecipeNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.recipe = recipe
            note.user = request.user  # Associates the note with the logged-in user
            note.is_public = False   # Forces the note to be private
            note.save()
            return redirect(recipe.get_absolute_url())
    else:
        form = RecipeNoteForm()
    context = {'form': form, 'recipe': recipe}
    return render(request, 'recipes/recipe_note_form.html', context)

# Recipe List view (for search functionality)
def recipe_list(request):
    query = request.GET.get('q')
    if query:
        recipes = Recipe.objects.filter(
            Q(title__icontains=query) | Q(ingredients__icontains=query)
        )
    else:
        recipes = Recipe.objects.all()
    return render(request, 'recipes/recipe_list.html', {'recipes': recipes})
