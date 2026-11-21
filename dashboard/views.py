
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser
from accounts.decorators import role_required
from .forms import WorkAssignmentForm, StaffAssignmentUpdateForm
from .forms import StaffCreationForm, StaffUpdateForm

from customers.models import WaterConnection
from django.db.models import Sum
from django.utils import timezone
from .models import WorkAssignment
from .forms import WorkAssignmentForm
from customers.models import WaterConnection, MeterReading
from billing.models import Bill
from complaints.models import Complaint
# =====================================================
# CUSTOMER DASHBOARD
# =====================================================

@role_required(CustomUser.Role.CUSTOMER)
def customer_dashboard(request):

    today = timezone.localdate()

    # Total customer water connections
    total_connections = WaterConnection.objects.filter(
        customer=request.user
    ).count()

    # Current month's water consumption
    monthly_consumption = MeterReading.objects.filter(
        connection__customer=request.user,
        reading_date__year=today.year,
        reading_date__month=today.month
    ).aggregate(
        total=Sum('consumption')
    )['total'] or 0

    # Pending and overdue bills
    pending_bills = Bill.objects.filter(
        connection__customer=request.user,
        status__in=[
            Bill.Status.PENDING,
            Bill.Status.OVERDUE
        ]
    ).count()

    # Recent customer bills
    recent_bills = Bill.objects.filter(
        connection__customer=request.user
    ).order_by('-generated_at')[:5]

    context = {
        'dashboard_title': 'Customer Dashboard',

        'customer_name': (
            request.user.first_name
            or request.user.username
        ),

        'total_connections': total_connections,
        'monthly_consumption': monthly_consumption,
        'pending_bills': pending_bills,

        # Complaints will be connected in the complaints phase.
        'open_complaints': None,
        'recent_complaints': [],

        'recent_bills': recent_bills,
    }

    return render(
        request,
        'dashboard/customer_dashboard.html',
        context
    )


# =====================================================
# STAFF DASHBOARD
# =====================================================

@role_required(CustomUser.Role.STAFF)
def staff_dashboard(request):

    # ---------------------------------------------
    # PHASE 10: WATER CONNECTION APPLICATIONS
    # ---------------------------------------------

    # Count applications waiting for staff approval.

    new_applications = WaterConnection.objects.filter(
        status=WaterConnection.Status.PENDING
    ).count()

    # Get the latest five customer applications.

    recent_applications = WaterConnection.objects.select_related(
        'customer'
    ).order_by('-submitted_at')[:5]

    # ---------------------------------------------
    # PHASE 11: METER READING MANAGEMENT
    # ---------------------------------------------

    # Count approved connections that do not have
    # any meter readings recorded yet.

    pending_readings = WaterConnection.objects.filter(
        status=WaterConnection.Status.APPROVED,
        meter_readings__isnull=True
    ).distinct().count()

    # ---------------------------------------------
    # STAFF DASHBOARD CONTEXT
    # ---------------------------------------------

    context = {
        'dashboard_title': 'Water Authority Staff Dashboard',

        'staff_name': (
            request.user.first_name
            or request.user.username
        ),

        # Phase 10 - Connection Applications
        'new_applications': new_applications,
        'recent_applications': recent_applications,

        # Phase 11 - Meter Readings
        'pending_readings': pending_readings,

        # Upcoming phases
        'pending_bills': None,
        'open_complaints': None,
        'recent_complaints': [],
    }

    return render(
        request,
        'dashboard/staff_dashboard.html',
        context
    )


# =====================================================
# MANAGER DASHBOARD
# =====================================================

@role_required(CustomUser.Role.MANAGER)
def manager_dashboard(request):

    # Count pending water connection applications
    pending_applications = WaterConnection.objects.filter(
        status=WaterConnection.Status.PENDING
    ).count()

    # Count open and in-progress complaints
    open_complaints = Complaint.objects.filter(
        status__in=[
            Complaint.Status.OPEN,
            Complaint.Status.IN_PROGRESS
        ]
    ).count()

    # Get the five latest customer applications
    recent_applications = WaterConnection.objects.select_related(
        'customer'
    ).order_by('-submitted_at')[:5]

    # Get the five latest complaints
    recent_complaints = Complaint.objects.select_related(
        'customer',
        'assigned_to'
    ).order_by('-submitted_at')[:5]

    # Get the five recently registered staff members
    recent_staff = CustomUser.objects.filter(
        role=CustomUser.Role.STAFF
    ).order_by('-date_joined')[:5]

    context = {
        'dashboard_title': 'Department Manager Dashboard',

        'manager_name': (
            request.user.first_name
            or request.user.username
        ),

        # Department statistics
        'total_customers': CustomUser.objects.filter(
            role=CustomUser.Role.CUSTOMER
        ).count(),

        'total_staff': CustomUser.objects.filter(
            role=CustomUser.Role.STAFF
        ).count(),

        'pending_applications': pending_applications,

        'open_complaints': open_complaints,

        # Recent activities
        'recent_applications': recent_applications,

        'recent_complaints': recent_complaints,

        'recent_staff': recent_staff,
    }

    return render(
        request,
        'dashboard/manager_dashboard.html',
        context
    )



# =====================================================
# HOME PAGE
# =====================================================

def home_view(request):

    if request.user.is_authenticated:

        if request.user.role == CustomUser.Role.CUSTOMER:
            return redirect('customer_dashboard')

        elif request.user.role == CustomUser.Role.STAFF:
            return redirect('staff_dashboard')

        elif request.user.role == CustomUser.Role.MANAGER:
            return redirect('manager_dashboard')

    return render(
        request,
        'dashboard/home.html'
    )


# =====================================================
# MANAGER: STAFF LIST
# =====================================================

@role_required(CustomUser.Role.MANAGER)
def staff_list(request):

    search_query = request.GET.get('q', '').strip()

    staff_members = CustomUser.objects.filter(
        role=CustomUser.Role.STAFF
    ).order_by('-date_joined')

    # Search by username, first name, last name or email.

    if search_query:

        staff_members = staff_members.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    context = {
        'staff_members': staff_members,
        'search_query': search_query,

        'total_staff': CustomUser.objects.filter(
            role=CustomUser.Role.STAFF
        ).count(),

        'active_staff': CustomUser.objects.filter(
            role=CustomUser.Role.STAFF,
            is_active=True
        ).count(),

        'inactive_staff': CustomUser.objects.filter(
            role=CustomUser.Role.STAFF,
            is_active=False
        ).count(),
    }

    return render(
        request,
        'dashboard/staff_list.html',
        context
    )


# =====================================================
# MANAGER: CREATE STAFF ACCOUNT
# =====================================================

@role_required(CustomUser.Role.MANAGER)
def staff_create(request):

    if request.method == 'POST':

        form = StaffCreationForm(request.POST)

        if form.is_valid():

            staff = form.save()

            messages.success(
                request,
                f'Staff account "{staff.username}" created successfully.'
            )

            return redirect('staff_list')

        else:

            messages.error(
                request,
                'Please correct the errors in the form.'
            )

    else:

        form = StaffCreationForm()

    return render(
        request,
        'dashboard/staff_form.html',
        {
            'form': form,
            'page_title': 'Create Staff Account',
            'button_text': 'Create Staff',
        }
    )


# =====================================================
# MANAGER: UPDATE STAFF ACCOUNT
# =====================================================

@role_required(CustomUser.Role.MANAGER)
def staff_update(request, staff_id):

    staff = get_object_or_404(
        CustomUser,
        id=staff_id,
        role=CustomUser.Role.STAFF
    )

    if request.method == 'POST':

        form = StaffUpdateForm(
            request.POST,
            instance=staff
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Staff details updated successfully.'
            )

            return redirect('staff_list')

        else:

            messages.error(
                request,
                'Please correct the errors in the form.'
            )

    else:

        form = StaffUpdateForm(
            instance=staff
        )

    return render(
        request,
        'dashboard/staff_form.html',
        {
            'form': form,
            'page_title': 'Update Staff Details',
            'button_text': 'Save Changes',
            'is_update': True,
        }
    )


# =====================================================
# MANAGER: ACTIVATE / DEACTIVATE STAFF
# =====================================================

@role_required(CustomUser.Role.MANAGER)
@require_POST
def staff_toggle_status(request, staff_id):

    staff = get_object_or_404(
        CustomUser,
        id=staff_id,
        role=CustomUser.Role.STAFF
    )

    staff.is_active = not staff.is_active

    staff.save(
        update_fields=['is_active']
    )

    if staff.is_active:

        messages.success(
            request,
            f'{staff.username} account activated successfully.'
        )

    else:

        messages.success(
            request,
            f'{staff.username} account deactivated successfully.'
        )

    return redirect('staff_list')


@login_required
@role_required(CustomUser.Role.MANAGER)
def create_assignment(request):

    if request.method == 'POST':
        form = WorkAssignmentForm(request.POST)

        if form.is_valid():
            assignment = form.save(commit=False)

            # Automatically record the logged-in Manager
            assignment.assigned_by = request.user

            # New tasks start as Assigned
            assignment.status = WorkAssignment.Status.ASSIGNED

            assignment.save()

            messages.success(
                request,
                f'Task "{assignment.title}" was assigned successfully.'
            )

            return redirect('assignment_list')

    else:
        form = WorkAssignmentForm()

    context = {
        'form': form,
        'page_title': 'Create Work Assignment',
    }

    return render(
        request,
        'dashboard/assignment_form.html',
        context
    )


@login_required
@role_required(CustomUser.Role.MANAGER)
def assignment_list(request):

    assignments = WorkAssignment.objects.select_related(
        'assigned_to',
        'assigned_by'
    ).all()

    # Search tasks by title or staff username
    search_query = request.GET.get('q', '').strip()

    if search_query:
        assignments = assignments.filter(
            title__icontains=search_query
        ) | assignments.filter(
            assigned_to__username__icontains=search_query
        )

    # Filter by status
    status_filter = request.GET.get('status', '')

    valid_statuses = [
        choice[0] for choice in WorkAssignment.Status.choices
    ]

    if status_filter in valid_statuses:
        assignments = assignments.filter(status=status_filter)

    # Statistics
    total_assignments = WorkAssignment.objects.count()

    pending_assignments = WorkAssignment.objects.filter(
        status=WorkAssignment.Status.ASSIGNED
    ).count()

    in_progress_assignments = WorkAssignment.objects.filter(
        status=WorkAssignment.Status.IN_PROGRESS
    ).count()

    completed_assignments = WorkAssignment.objects.filter(
        status=WorkAssignment.Status.COMPLETED
    ).count()

    overdue_assignments = WorkAssignment.objects.filter(
        deadline__lt=timezone.localdate()
    ).exclude(
        status__in=[
            WorkAssignment.Status.COMPLETED,
            WorkAssignment.Status.CANCELLED
        ]
    ).count()

    context = {
        'assignments': assignments,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': WorkAssignment.Status.choices,

        'total_assignments': total_assignments,
        'pending_assignments': pending_assignments,
        'in_progress_assignments': in_progress_assignments,
        'completed_assignments': completed_assignments,
        'overdue_assignments': overdue_assignments,
    }

    return render(
        request,
        'dashboard/assignment_list.html',
        context
    )


@login_required
@role_required(CustomUser.Role.MANAGER)
def edit_assignment(request, assignment_id):

    assignment = get_object_or_404(
        WorkAssignment,
        id=assignment_id
    )

    if request.method == 'POST':
        form = WorkAssignmentForm(
            request.POST,
            instance=assignment
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Work assignment updated successfully.'
            )

            return redirect('assignment_list')

    else:
        form = WorkAssignmentForm(instance=assignment)

    context = {
        'form': form,
        'assignment': assignment,
        'page_title': 'Edit Work Assignment',
    }

    return render(
        request,
        'dashboard/assignment_form.html',
        context
    )




@login_required
@role_required(CustomUser.Role.STAFF)
def my_assignments(request):

    assignments = WorkAssignment.objects.filter(
        assigned_to=request.user
    ).order_by('deadline', '-created_at')

    # Filter assignments by status
    status_filter = request.GET.get('status', '')

    valid_statuses = [
        choice[0] for choice in WorkAssignment.Status.choices
    ]

    if status_filter in valid_statuses:
        assignments = assignments.filter(status=status_filter)

    # Staff task statistics
    total_assignments = WorkAssignment.objects.filter(
        assigned_to=request.user
    ).count()

    pending_assignments = WorkAssignment.objects.filter(
        assigned_to=request.user,
        status=WorkAssignment.Status.ASSIGNED
    ).count()

    in_progress_assignments = WorkAssignment.objects.filter(
        assigned_to=request.user,
        status=WorkAssignment.Status.IN_PROGRESS
    ).count()

    completed_assignments = WorkAssignment.objects.filter(
        assigned_to=request.user,
        status=WorkAssignment.Status.COMPLETED
    ).count()

    overdue_assignments = WorkAssignment.objects.filter(
        assigned_to=request.user,
        deadline__lt=timezone.localdate()
    ).exclude(
        status__in=[
            WorkAssignment.Status.COMPLETED,
            WorkAssignment.Status.CANCELLED
        ]
    ).count()

    context = {
        'assignments': assignments,
        'status_filter': status_filter,
        'status_choices': WorkAssignment.Status.choices,

        'total_assignments': total_assignments,
        'pending_assignments': pending_assignments,
        'in_progress_assignments': in_progress_assignments,
        'completed_assignments': completed_assignments,
        'overdue_assignments': overdue_assignments,
    }

    return render(
        request,
        'dashboard/my_assignments.html',
        context
    )


@login_required
@role_required(CustomUser.Role.STAFF)
def update_my_assignment(request, assignment_id):

    assignment = get_object_or_404(
        WorkAssignment,
        id=assignment_id,
        assigned_to=request.user
    )

    # Cancelled tasks cannot be updated
    if assignment.status == WorkAssignment.Status.CANCELLED:
        messages.error(
            request,
            'Cancelled assignments cannot be updated.'
        )
        return redirect('my_assignments')

    if request.method == 'POST':

        form = StaffAssignmentUpdateForm(
            request.POST,
            instance=assignment
        )

        if form.is_valid():

            updated_assignment = form.save(commit=False)

            # Record completion time
            if (
                updated_assignment.status
                == WorkAssignment.Status.COMPLETED
            ):
                if not updated_assignment.completed_at:
                    updated_assignment.completed_at = timezone.now()

            else:
                updated_assignment.completed_at = None

            updated_assignment.save()

            messages.success(
                request,
                'Your task progress has been updated successfully.'
            )

            return redirect('my_assignments')

    else:
        form = StaffAssignmentUpdateForm(instance=assignment)

    context = {
        'form': form,
        'assignment': assignment,
        'page_title': 'Update Task Progress',
    }

    return render(
        request,
        'dashboard/update_my_assignment.html',
        context
    )