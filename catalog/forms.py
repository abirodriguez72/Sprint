from django import forms
from django.contrib.auth.hashers import make_password
from .models import User, Recipe, Review, 
from .models import RecipeNote

class UserProfileCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['real_name', 'email', 'user_name', 'password', 'confirm_password', 'bio', 'profile_pic', 'user_type']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Hash the password before saving
        user.password = make_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class UserLoginForm(forms.Form):
    user_name = forms.CharField(label="Username", max_length=100)
    password = forms.CharField(widget=forms.PasswordInput, label="Password")


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'ingredients', 'instructions', 'notes', 'category', 'photo', 'rating',]
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
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_category(self):
        # Ensure that at least one category is selected.
        categories = self.cleaned_data.get('category')
        if not categories:
            raise forms.ValidationError("Please select at least one category.")
        return categories



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(),  # Django will use the RATING_CHOICES defined in your model
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your review here'}),
        }
class RecipeNoteForm(forms.ModelForm):
    class Meta:
        model = RecipeNote
        fields = ['note', 'is_public']

