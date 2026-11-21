from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from accounts.models import CustomUser
from .models import WorkAssignment


# ==========================================
# STAFF CREATION FORM
# ==========================================

class StaffCreationForm(UserCreationForm):

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

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control'
            })

        self.fields['username'].help_text = ''

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password',
        })

        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password',
        })

        self.fields['password1'].help_text = (
            'Use a strong password with at least 8 characters.'
        )

    def save(self, commit=True):
        staff = super().save(commit=False)

        # Assign the STAFF role automatically
        staff.role = CustomUser.Role.STAFF
        staff.is_active = True

        if commit:
            staff.save()

        return staff


# ==========================================
# STAFF UPDATE FORM
# ==========================================

class StaffUpdateForm(forms.ModelForm):

    class Meta:
        model = CustomUser

        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'address',
            'is_active',
        ]

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
            }),

            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
            }),

            'email': forms.EmailInput(attrs={
                'class': 'form-control',
            }),

            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
            }),

            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
            }),

            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


# ==========================================
# WORK ASSIGNMENT CREATION FORM
# ==========================================

class WorkAssignmentForm(forms.ModelForm):

    class Meta:
        model = WorkAssignment

        fields = [
            'title',
            'description',
            'assigned_to',
            'priority',
            'deadline',
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title',
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the task in detail',
            }),

            'assigned_to': forms.Select(attrs={
                'class': 'form-select',
            }),

            'priority': forms.Select(attrs={
                'class': 'form-select',
            }),

            'deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only active Staff accounts should appear
        self.fields['assigned_to'].queryset = CustomUser.objects.filter(
            role=CustomUser.Role.STAFF,
            is_active=True
        ).order_by('username')

        self.fields['assigned_to'].label = 'Assign to Staff'
        self.fields['deadline'].label = 'Task Deadline'

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')

        if deadline and deadline < timezone.localdate():
            raise forms.ValidationError(
                'The deadline cannot be in the past.'
            )

        return deadline


# ==========================================
# STAFF ASSIGNMENT PROGRESS UPDATE FORM
# ==========================================

class StaffAssignmentUpdateForm(forms.ModelForm):

    class Meta:
        model = WorkAssignment

        fields = [
            'status',
            'staff_remarks',
        ]

        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),

            'staff_remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your work progress or updates',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Staff cannot cancel or reassign their own tasks
        self.fields['status'].choices = [
            (
                WorkAssignment.Status.IN_PROGRESS,
                'In Progress'
            ),
            (
                WorkAssignment.Status.COMPLETED,
                'Completed'
            ),
            (
                WorkAssignment.Status.ON_HOLD,
                'On Hold'
            ),
        ]

        self.fields['status'].label = 'Task Status'
        self.fields['staff_remarks'].label = 'Progress Remarks'