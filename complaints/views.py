
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from accounts.decorators import role_required
from accounts.models import CustomUser
from .models import Complaint
from .forms import ComplaintForm, ComplaintUpdateForm


def staff_or_manager_required(user):
    return (
        user.is_authenticated
        and user.role in [
            CustomUser.Role.STAFF,
            CustomUser.Role.MANAGER
        ]
    )


# CUSTOMER: Submit a complaint
@login_required
@role_required('CUSTOMER')
def submit_complaint(request):

    if request.method == 'POST':
        form = ComplaintForm(request.POST)

        if form.is_valid():
            complaint = form.save(commit=False)

            # Customer is assigned from the logged-in account
            complaint.customer = request.user
            complaint.save()

            messages.success(
                request,
                f'Complaint submitted successfully. '
                f'Reference: {complaint.complaint_number}'
            )

            return redirect('my_complaints')

    else:
        form = ComplaintForm()

    return render(
        request,
        'complaints/submit_complaint.html',
        {'form': form}
    )


# CUSTOMER: View their own complaints
@login_required
@role_required('CUSTOMER')
def my_complaints(request):

    complaints = Complaint.objects.filter(
        customer=request.user
    )

    context = {
        'complaints': complaints,
        'total_complaints': complaints.count(),
        'open_complaints': complaints.filter(
            status=Complaint.Status.OPEN
        ).count(),
        'in_progress_complaints': complaints.filter(
            status=Complaint.Status.IN_PROGRESS
        ).count(),
        'resolved_complaints': complaints.filter(
            status=Complaint.Status.RESOLVED
        ).count(),
    }

    return render(
        request,
        'complaints/my_complaints.html',
        context
    )


# CUSTOMER / STAFF / MANAGER: View complaint details
@login_required
def complaint_detail(request, complaint_id):

    complaint = get_object_or_404(
        Complaint.objects.select_related(
            'customer',
            'assigned_to'
        ),
        id=complaint_id
    )

    if request.user.role == CustomUser.Role.CUSTOMER:
        # Customers can only view their own complaints
        if complaint.customer_id != request.user.id:
            raise PermissionDenied(
                'You cannot view another customer complaint.'
            )

    elif not staff_or_manager_required(request.user):
        raise PermissionDenied(
            'You do not have permission to view this complaint.'
        )

    return render(
        request,
        'complaints/complaint_detail.html',
        {'complaint': complaint}
    )


# STAFF / MANAGER: View all complaints
@login_required
def staff_complaint_list(request):

    if not staff_or_manager_required(request.user):
        raise PermissionDenied(
            'Only staff or managers can access complaints management.'
        )

    complaints = Complaint.objects.select_related(
        'customer',
        'assigned_to'
    )

    status_filter = request.GET.get('status', '')

    if status_filter in Complaint.Status.values:
        complaints = complaints.filter(status=status_filter)

    context = {
        'complaints': complaints,
        'total_complaints': Complaint.objects.count(),
        'open_complaints': Complaint.objects.filter(
            status=Complaint.Status.OPEN
        ).count(),
        'in_progress_complaints': Complaint.objects.filter(
            status=Complaint.Status.IN_PROGRESS
        ).count(),
        'resolved_complaints': Complaint.objects.filter(
            status=Complaint.Status.RESOLVED
        ).count(),
        'status_filter': status_filter,
    }

    return render(
        request,
        'complaints/staff_complaint_list.html',
        context
    )


# STAFF / MANAGER: Update complaint
@login_required
def update_complaint(request, complaint_id):

    if not staff_or_manager_required(request.user):
        raise PermissionDenied(
            'Only staff or managers can update complaints.'
        )

    complaint = get_object_or_404(
        Complaint,
        id=complaint_id
    )

    if request.method == 'POST':

        form = ComplaintUpdateForm(
            request.POST,
            instance=complaint
        )

        if form.is_valid():

            updated_complaint = form.save(commit=False)

            if updated_complaint.status in [
                Complaint.Status.RESOLVED,
                Complaint.Status.CLOSED
            ]:
                if not updated_complaint.resolved_at:
                    updated_complaint.resolved_at = timezone.now()
            else:
                updated_complaint.resolved_at = None

            updated_complaint.save()

            messages.success(
                request,
                'Complaint updated successfully.'
            )

            return redirect(
                'complaint_detail',
                complaint_id=complaint.id
            )

    else:
        form = ComplaintUpdateForm(instance=complaint)

    return render(
        request,
        'complaints/update_complaint.html',
        {
            'form': form,
            'complaint': complaint
        }
    )
