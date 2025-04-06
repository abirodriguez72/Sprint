from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic, View
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from .models import Recipe, Category, User, Review
from .forms import UserProfileCreationForm, UserLoginForm, RecipeForm, ReviewForm
from .decorators import group_required

# Home view: Displays recent recipes and top-level categories.
def home(request):
    recent_recipes = Recipe.objects.order_by('-created_at')[:6]
    top_categories = Category.objects.filter(parent=None)

    # Displays number of recipes, reviews, users, and visits.

    num_recipes = Recipe.objects.count()
    num_reviews = Review.objects.count()
    num_users = User.objects.count()

    # Number of visits to this view, as counted in the session variable.
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


# Recipe List View: Uses Django's generic ListView.
class RecipeListView(generic.ListView):
    model = Recipe
    template_name = 'recipes/recipe_list.html'
    context_object_name = 'recipes'
    paginate_by = 10  # Display 10 recipes per page


# Recipe Detail View: Uses Django's generic DetailView and includes reviews.
class RecipeDetailView(generic.DetailView):
    model = Recipe
    template_name = 'recipes/recipe_details.html'
    context_object_name = 'recipe'

    def get_context_data(self, **kwargs):
        # Extend context to include reviews for this recipe.
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.all()
        return context


# Category Detail View: Displays a category, its subcategories, and its recipes.
def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    # Filter recipes associated with this category.
    recipes = Recipe.objects.filter(category=category)
    subcategories = category.subcategories.all()
    context = {
        'category': category,
        'recipes': recipes,
        'subcategories': subcategories,
    }
    return render(request, 'categories/category_details.html', context)

# User Profile Form view: Allows users to create profiles.
def create_user_profile(request):
    if request.method == 'POST':
        form = UserProfileCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')  # Change to your desired URL name
    else:
        form = UserProfileCreationForm()
    return render(request, 'users/signup.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = UserProfileCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Optionally, log the user in by storing their user_id in the session
            request.session['user_id'] = str(user.user_id)
            # Redirect to the user's profile page after sign-up
            return redirect('user_detail', user_id=user.user_id)
    else:
        form = UserProfileCreationForm()
    return render(request, 'users/signup.html', {'form': form})

def login_view(request):
    error = None
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['user_name']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(user_name=username)
                if check_password(password, user.password):
                    # Log the user in by storing their user_id in the session.
                    request.session['user_id'] = str(user.user_id)
                    # Redirect to the user's profile page after login
                    return redirect('user_detail', user_id=user.user_id)
                else:
                    error = "Invalid username or password"
            except User.DoesNotExist:
                error = "Invalid username or password"
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form, 'error': error})


# User Detail View: Displays a user profile and the recipes they have posted.
def user_detail(request, user_id):
    user = get_object_or_404(User, user_id=user_id)
    recipes = Recipe.objects.filter(user=user)
    reviews = Review.objects.filter(user=user)
    context = {
        'user': user,
        'recipes': recipes,
        'reviews': reviews,
    }
    return render(request, 'users/user_details.html', context)

def create_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            # Set the user field from the logged-in user (adjust according to your auth method)
            recipe.user = request.user  # or however you retrieve the current user
            recipe.save()
            # Save many-to-many fields after saving the recipe
            form.save_m2m()
            return redirect(recipe.get_absolute_url())
    else:
        form = RecipeForm()
    return render(request, 'recipes/recipe_form.html', {'form': form})


def create_review(request, recipe_id):
    recipe = get_object_or_404(Recipe, recipe_id=recipe_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            # Set the recipe and the logged-in user
            review.recipe = recipe
            review.user = request.user  # Adjust if you're not using Django's auth system
            review.save()
            return redirect(recipe.get_absolute_url())
    else:
        form = ReviewForm()
    return render(request, 'recipes/review_form.html', {'form': form, 'recipe': recipe})

def recipe_list(request):
    query = request.GET.get('q')
    if query:
        recipes = Recipe.objects.filter(
            Q(title__icontains=query) | Q(ingredients__icontains=query)
        )
    else:
        recipes = Recipe.objects.all()
    return render(request, 'recipes/recipe_list.html', {'recipes': recipes})
