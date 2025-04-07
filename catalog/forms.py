from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User  # Using Django's default user model
from .models import Profile, Recipe, Review, RecipeNote


# Form to create a new User using Django's built-in UserCreationForm
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


# Form to create or update a Profile (with extended user information)
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["real_name", "bio", "profile_pic", "user_type"]



class UserLoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, label="Password")


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        # If you still want to include the rating field in Recipe, otherwise remove it
        fields = ['title', 'ingredients', 'instructions', 'notes', 'category', 'photo', 'rating']
        widgets = {
            'ingredients': forms.Textarea(attrs={
                'rows': 6,
                'cols': 80,
                'placeholder': 'List each ingredient on a new line, e.g.,&#10;4 tbsp sugar&#10;2 cups flour'
            }),
            'instructions': forms.Textarea(attrs={
                'rows': 10,
                'cols': 80,
                'placeholder': 'Enter step-by-step instructions, separating steps with a new line, e.g.,&#10;Step 1: Preheat oven&#10;Step 2: Mix ingredients'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'cols': 80,
                'placeholder': 'Any additional notes (optional)'
            }),
            'category': forms.CheckboxSelectMultiple(),
            'rating': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_category(self):
        categories = self.cleaned_data.get('category')
        if not categories:
            raise forms.ValidationError("Please select at least one category.")
        return categories


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(),  # Uses RATING_CHOICES from the model
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your review here'}),
        }


class RecipeNoteForm(forms.ModelForm):
    class Meta:
        model = RecipeNote
        fields = ['note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your private note here'}),
        }
