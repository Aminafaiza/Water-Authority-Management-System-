
from django import forms
from django.utils import timezone

from .models import Payment

from .models import Tariff


class PaymentSubmissionForm(forms.ModelForm):

    class Meta:
        model = Payment

        fields = [
            'payment_method',
            'transaction_reference',
            'payment_date',
        ]

        widgets = {
            'payment_method': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'transaction_reference': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter transaction reference'
                }
            ),

            'payment_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
        }

    def clean_transaction_reference(self):

        reference = self.cleaned_data.get(
            'transaction_reference'
        )

        reference = reference.strip()

        if Payment.objects.filter(
            transaction_reference__iexact=reference
        ).exists():

            raise forms.ValidationError(
                'This transaction reference has already been submitted.'
            )

        return reference

    def clean_payment_date(self):

        payment_date = self.cleaned_data.get('payment_date')

        if payment_date and payment_date > timezone.localdate():

            raise forms.ValidationError(
                'Payment date cannot be in the future.'
            )

        return payment_date




class TariffForm(forms.ModelForm):

    class Meta:
        model = Tariff

        fields = [
            'connection_type',
            'rate_per_unit',
            'fixed_charge',
        ]

        widgets = {
            'connection_type': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'rate_per_unit': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter rate per unit',
                    'min': '0',
                    'step': '0.01'
                }
            ),

            'fixed_charge': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter fixed charge',
                    'min': '0',
                    'step': '0.01'
                }
            ),
        }

    def clean_rate_per_unit(self):
        rate = self.cleaned_data['rate_per_unit']

        if rate < 0:
            raise forms.ValidationError(
                'Rate per unit cannot be negative.'
            )

        return rate

    def clean_fixed_charge(self):
        charge = self.cleaned_data['fixed_charge']

        if charge < 0:
            raise forms.ValidationError(
                'Fixed charge cannot be negative.'
            )

        return charge
