
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomerRegistrationForm(UserCreationForm):

    class Meta:
        model = CustomUser

        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'address',
        ]

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter username',
                'autocomplete': 'username',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter address',
                'rows': 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].help_text = ''

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password',
            'autocomplete': 'new-password',
        })

        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'autocomplete': 'new-password',
        })

        self.fields['password1'].help_text = (
            'Use at least 8 characters. Avoid common or entirely numeric passwords.'
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.Role.CUSTOMER

        if commit:
            user.save()

        return user
