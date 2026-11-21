
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class WaterConnection(models.Model):

    class ConnectionType(models.TextChoices):
        DOMESTIC = 'DOMESTIC', 'Domestic'
        COMMERCIAL = 'COMMERCIAL', 'Commercial'
        INDUSTRIAL = 'INDUSTRIAL', 'Industrial'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='water_connections'
    )

    connection_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True
    )

    applicant_name = models.CharField(max_length=150)

    contact_number = models.CharField(max_length=15)

    property_address = models.TextField()

    connection_type = models.CharField(
        max_length=20,
        choices=ConnectionType.choices,
        default=ConnectionType.DOMESTIC
    )

    purpose = models.TextField(
        help_text='Explain why you need this water connection.'
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    staff_remarks = models.TextField(blank=True)

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_water_connections'
    )

    submitted_at = models.DateTimeField(auto_now_add=True)

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return (
            self.connection_number
            or f'Application #{self.pk}'
        )

    def approve(self, staff_user):
        if self.status != self.Status.PENDING:
            raise ValueError(
                'Only pending applications can be approved.'
            )

        self.status = self.Status.APPROVED
        self.reviewed_by = staff_user
        self.reviewed_at = timezone.now()

        if not self.connection_number:
            self.connection_number = f'AC-{self.pk:06d}'

        self.save(
            update_fields=[
                'status',
                'reviewed_by',
                'reviewed_at',
                'connection_number',
            ]
        )

    def reject(self, staff_user, remarks):
        if self.status != self.Status.PENDING:
            raise ValueError(
                'Only pending applications can be rejected.'
            )

        self.status = self.Status.REJECTED
        self.reviewed_by = staff_user
        self.reviewed_at = timezone.now()
        self.staff_remarks = remarks

        self.save(
            update_fields=[
                'status',
                'reviewed_by',
                'reviewed_at',
                'staff_remarks',
            ]
        )




class MeterReading(models.Model):

    connection = models.ForeignKey(
        'customers.WaterConnection',
        on_delete=models.CASCADE,
        related_name='meter_readings'
    )

    previous_reading = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    current_reading = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    consumption = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    reading_date = models.DateField(
        default=timezone.localdate
    )

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_meter_readings'
    )

    remarks = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-reading_date', '-id']
        constraints = [
            models.UniqueConstraint(
                fields=['connection', 'reading_date'],
                name='unique_connection_reading_date'
            )
        ]

    def clean(self):
        if self.current_reading < self.previous_reading:
            raise ValidationError({
                'current_reading':
                    'Current reading cannot be less than previous reading.'
            })

        if self.connection_id:
            if self.connection.status != WaterConnection.Status.APPROVED:
                raise ValidationError(
                    'Meter readings can only be recorded for approved connections.'
                )

            previous = MeterReading.objects.filter(
                connection=self.connection
            ).exclude(pk=self.pk).order_by(
                '-reading_date', '-id'
            ).first()

            if previous:
                if self.reading_date < previous.reading_date:
                    raise ValidationError({
                        'reading_date':
                            'Reading date cannot be earlier than the previous recorded date.'
                    })

                if self.current_reading < previous.current_reading:
                    raise ValidationError({
                        'current_reading':
                            'Current reading must not be less than the last recorded reading.'
                    })

    def save(self, *args, **kwargs):
        self.consumption = (
            self.current_reading - self.previous_reading
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f'{self.connection.connection_number} - '
            f'{self.reading_date}'
        )
