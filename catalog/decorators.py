from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

def group_required(group_name):
    """
    Decorator checks whether the logged-in user belongs to a given group.
    If not, redirects to the login page or raises PermissionDenied.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')  # Adjust the URL name as needed.
            if request.user.groups.filter(name=group_name).exists():
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("You do not have permission to access this page.")
        return _wrapped_view
    return decorator
