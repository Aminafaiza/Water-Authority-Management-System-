
from django import forms
from accounts.models import CustomUser
from .models import Complaint


class ComplaintForm(forms.ModelForm):

    class Meta:
        model = Complaint

        fields = [
            'category',
            'subject',
            'description',
        ]

        widgets = {
            'category': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'subject': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter complaint subject'
                }
            ),

            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5,
                    'placeholder': 'Explain your complaint clearly'
                }
            ),
        }


class ComplaintUpdateForm(forms.ModelForm):

    class Meta:
        model = Complaint

        fields = [
            'status',
            'priority',
            'assigned_to',
            'staff_remarks',
        ]

        widgets = {
            'status': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'priority': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'assigned_to': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'staff_remarks': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Enter staff remarks or resolution details'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['assigned_to'].queryset = (
            CustomUser.objects.filter(
                role=CustomUser.Role.STAFF,
                is_active=True
            ).order_by('username')
        )

        self.fields['assigned_to'].required = False
