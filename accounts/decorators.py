from django.contrib.auth.decorators import login_required
from functools import wraps
from django.views.decorators.cache import never_cache
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def role_required(*required_roles):

    def decorator(view_func):
        @login_required
        @never_cache
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            # Check authentication
            if not request.user.is_authenticated:
                return redirect('login')

            # Check whether the user has an allowed role
            if request.user.role not in required_roles:
                raise PermissionDenied(
                    "You do not have permission to access this page."
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
