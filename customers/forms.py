
from django import forms
from .models import WaterConnection
from django.utils import timezone
from .models import MeterReading


class WaterConnectionForm(forms.ModelForm):

    class Meta:
        model = WaterConnection
        fields = [
            'applicant_name',
            'contact_number',
            'property_address',
            'connection_type',
            'purpose',
        ]

        widgets = {
            'applicant_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter applicant name',
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact number',
            }),
            'property_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter complete property address',
            }),
            'connection_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'purpose': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Explain the purpose of this connection',
            }),
        }

    def clean_contact_number(self):
        number = self.cleaned_data['contact_number'].strip()

        if not number.isdigit() or not 10 <= len(number) <= 15:
            raise forms.ValidationError(
                'Enter a valid contact number using 10 to 15 digits.'
            )

        return number






class MeterReadingForm(forms.ModelForm):

    class Meta:
        model = MeterReading

        fields = [
            'current_reading',
            'reading_date',
            'remarks',
        ]

        widgets = {
            'current_reading': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter current meter reading',
                'step': '0.01',
                'min': '0',
            }),

            'reading_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),

            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter remarks (optional)',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk and not self.initial.get('reading_date'):
            self.fields['reading_date'].initial = timezone.localdate()

    def clean(self):
        cleaned_data = super().clean()

        current_reading = cleaned_data.get('current_reading')
        reading_date = cleaned_data.get('reading_date')
        connection = self.instance.connection

        if not connection:
            raise forms.ValidationError(
                'Please select a water connection.'
            )

        if connection.status != connection.Status.APPROVED:
            raise forms.ValidationError(
                'Only approved connections can have meter readings.'
            )

        previous = MeterReading.objects.filter(
            connection=connection
        ).order_by('-reading_date', '-id').first()

        if previous:
            if reading_date and reading_date < previous.reading_date:
                self.add_error(
                    'reading_date',
                    'The reading date cannot be earlier than the last reading.'
                )

            if (
                current_reading is not None
                and current_reading < previous.current_reading
            ):
                self.add_error(
                    'current_reading',
                    'Enter a value greater than or equal to the last reading.'
                )

        return cleaned_data
def clean_reading_date(self):

    reading_date = self.cleaned_data.get('reading_date')

    if reading_date and self.instance.connection_id:

        duplicate = MeterReading.objects.filter(
            connection=self.instance.connection,
            reading_date=reading_date
        ).exclude(
            pk=self.instance.pk
        ).exists()

        if duplicate:
            raise forms.ValidationError(
                "A meter reading for this connection "
                "has already been recorded on this date. "
                "Please select another date."
            )

    return reading_date