from django.conf import settings
from django.db import models


class WorkAssignment(models.Model):

    # Task status options
    class Status(models.TextChoices):
        ASSIGNED = 'ASSIGNED', 'Assigned'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        ON_HOLD = 'ON_HOLD', 'On Hold'
        CANCELLED = 'CANCELLED', 'Cancelled'

    # Task priority options
    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        URGENT = 'URGENT', 'Urgent'

    # Task information
    title = models.CharField(max_length=200)

    description = models.TextField()

    # Staff member who receives the task
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='work_assignments'
    )

    # Manager who creates the assignment
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_assignments'
    )

    # Task priority
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )

    # Task progress status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ASSIGNED
    )

    # Task deadline
    deadline = models.DateField()

    # Remarks added by staff
    staff_remarks = models.TextField(blank=True)

    # Task creation time
    created_at = models.DateTimeField(auto_now_add=True)

    # Completion time
    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['deadline', '-created_at']

    def __str__(self):
        return f'{self.title} - {self.assigned_to.username}'