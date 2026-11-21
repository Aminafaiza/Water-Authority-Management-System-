
from django.conf import settings
from django.db import models
from django.utils import timezone


class Complaint(models.Model):

    class Category(models.TextChoices):
        WATER_SUPPLY = 'WATER_SUPPLY', 'Water Supply Issue'
        LEAKAGE = 'LEAKAGE', 'Water Leakage'
        BILLING = 'BILLING', 'Billing Issue'
        METER = 'METER', 'Meter Problem'
        QUALITY = 'QUALITY', 'Water Quality Issue'
        OTHER = 'OTHER', 'Other'

    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        URGENT = 'URGENT', 'Urgent'

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='complaints'
    )

    complaint_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True
    )

    category = models.CharField(
        max_length=30,
        choices=Category.choices
    )

    subject = models.CharField(max_length=200)

    description = models.TextField()

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_complaints'
    )

    staff_remarks = models.TextField(blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.complaint_number:
            self.complaint_number = f'AC-CMP-{self.pk:06d}'
            super().save(update_fields=['complaint_number'])

    def __str__(self):
        return self.complaint_number or f'Complaint #{self.pk}'
