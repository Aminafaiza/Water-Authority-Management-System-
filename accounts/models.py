
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):

    class Role(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'Customer'
        STAFF = 'STAFF', 'Water Authority Staff'
        MANAGER = 'MANAGER', 'Department Manager'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    address = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"



