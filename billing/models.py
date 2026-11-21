
from django.conf import settings
from django.db import models
from customers.models import WaterConnection, MeterReading
from django.db.models import Q
from django.utils import timezone

class Bill(models.Model):

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PAID = 'PAID', 'Paid'
        OVERDUE = 'OVERDUE', 'Overdue'

    # One meter reading can generate only one bill.
    meter_reading = models.OneToOneField(
        MeterReading,
        on_delete=models.PROTECT,
        related_name='bill'
    )

    connection = models.ForeignKey(
        WaterConnection,
        on_delete=models.PROTECT,
        related_name='bills'
    )

    payment_number = models.CharField(
    max_length=30,
    unique=True,
    blank=True,
    null=True,
    default=None
)

    billing_period_start = models.DateField()
    billing_period_end = models.DateField()

    consumption = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    rate_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    fixed_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    due_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_bills'
    )

    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-generated_at']

    def save(self, *args, **kwargs):

        # Calculate the total amount automatically.
        self.total_amount = (
            self.consumption * self.rate_per_unit
        ) + self.fixed_charge

        super().save(*args, **kwargs)

    def __str__(self):
        return self.bill_number or f'Bill #{self.pk}'



class Payment(models.Model):

    class PaymentMethod(models.TextChoices):
        UPI = 'UPI', 'UPI'
        BANK_TRANSFER = 'BANK_TRANSFER', 'Bank Transfer'
        CASH = 'CASH', 'Cash'
        OTHER = 'OTHER', 'Other'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Verification'
        VERIFIED = 'VERIFIED', 'Verified'
        REJECTED = 'REJECTED', 'Rejected'

    bill = models.ForeignKey(
        'billing.Bill',
        on_delete=models.PROTECT,
        related_name='payments'
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='payments'
    )

    payment_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True,
        default=None
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices
    )

    transaction_reference = models.CharField(
        max_length=100,
        unique=True
    )

    payment_date = models.DateField(
        default=timezone.localdate
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_payments'
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True
    )

    staff_remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name='payment_amount_greater_than_zero'
            ),

            models.UniqueConstraint(
                fields=['bill'],
                condition=Q(status='VERIFIED'),
                name='one_verified_payment_per_bill'
            ),
        ]

    def __str__(self):
        return self.payment_number or f'Payment #{self.pk}'


# =====================================================
# TARIFF CONFIGURATION
# =====================================================

class Tariff(models.Model):

    connection_type = models.CharField(
        max_length=20,
        choices=WaterConnection.ConnectionType.choices,
        unique=True
    )

    rate_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    fixed_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_tariffs'
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['connection_type']

    def __str__(self):
        return f'{self.get_connection_type_display()} Tariff'