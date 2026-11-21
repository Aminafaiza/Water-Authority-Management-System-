
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_POST

from .forms import CustomerRegistrationForm
from .models import CustomUser
from django.contrib.auth import logout

def get_role_redirect(user):

    if user.role == CustomUser.Role.CUSTOMER:
        return 'customer_dashboard'

    elif user.role == CustomUser.Role.STAFF:
        return 'staff_dashboard'

    elif user.role == CustomUser.Role.MANAGER:
        return 'manager_dashboard'

    return 'login'


def register_view(request):

    # Already logged-in users should not register again
    if request.user.is_authenticated:
        return redirect(get_role_redirect(request.user))

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Registration successful! Please log in.'
            )

            return redirect('login')

        else:
            messages.error(
                request,
                'Please correct the errors below.'
            )

    else:
        form = CustomerRegistrationForm()

    return render(
        request,
        'accounts/register.html',
        {'form': form}
    )

def login_view(request):

    if request.user.is_authenticated:
        return redirect(get_role_redirect(request.user))

    if request.method == 'POST':

        form = AuthenticationForm(
            request=request,
            data=request.POST
        )

        selected_role = request.POST.get('selected_role')

        if form.is_valid():

            user = form.get_user()

            allowed_roles = [
                CustomUser.Role.CUSTOMER,
                CustomUser.Role.STAFF,
                CustomUser.Role.MANAGER,
            ]

            if selected_role not in allowed_roles:
                messages.error(
                    request,
                    'Please select a valid account type.'
                )

            elif user.role != selected_role:
                messages.error(
                    request,
                    'The selected account type does not match your account.'
                )

            else:
                auth_login(request, user)

                messages.success(
                    request,
                    f'Welcome, {user.first_name or user.username}!'
                )

                return redirect(get_role_redirect(user))

        else:
            messages.error(
                request,
                'Invalid username or password. Please try again.'
            )

    else:
        form = AuthenticationForm()

    form.fields['username'].widget.attrs.update({
        'class': 'form-control',
        'placeholder': 'Enter your username',
        'autocomplete': 'username',
    })

    form.fields['password'].widget.attrs.update({
        'class': 'form-control',
        'placeholder': 'Enter your password',
        'autocomplete': 'current-password',
    })

    return render(
        request,
        'accounts/login.html',
        {
            'form': form,
        }
    )


@require_POST
def logout_view(request):

    auth_logout(request)

    messages.success(
        request,
        'You have successfully logged out.'
    )

    return redirect('login')

