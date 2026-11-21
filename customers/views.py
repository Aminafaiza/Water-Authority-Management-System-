
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from accounts.models import CustomUser
from accounts.decorators import role_required

from .models import WaterConnection, MeterReading
from .forms import WaterConnectionForm , MeterReadingForm

def staff_or_manager_required(user):
    return (
        user.is_authenticated
        and user.role in [
            CustomUser.Role.STAFF,
            CustomUser.Role.MANAGER
        ]
    )
# CUSTOMER: Submit a new connection application
@role_required(CustomUser.Role.CUSTOMER)
def apply_connection(request):

    if request.method == 'POST':
        form = WaterConnectionForm(request.POST)

        if form.is_valid():
            connection = form.save(commit=False)

            # Link the application to the logged-in customer.
            connection.customer = request.user
            connection.save()

            messages.success(
                request,
                'Your water connection application was submitted successfully.'
            )

            return redirect('my_connections')

    else:
        form = WaterConnectionForm(initial={
            'applicant_name': request.user.get_full_name()
            or request.user.username,
            'contact_number': request.user.phone_number or '',
            'property_address': request.user.address or '',
        })

    return render(
        request,
        'customers/apply_connection.html',
        {'form': form}
    )


# CUSTOMER: View only their own applications
@role_required(CustomUser.Role.CUSTOMER)
def my_connections(request):

    connections = WaterConnection.objects.filter(
        customer=request.user
    )

    return render(
        request,
        'customers/my_connections.html',
        {'connections': connections}
    )


# CUSTOMER: View one of their own applications
@role_required(CustomUser.Role.CUSTOMER)
def connection_detail(request, connection_id):

    connection = get_object_or_404(
        WaterConnection,
        id=connection_id,
        customer=request.user
    )

    return render(
        request,
        'customers/connection_detail.html',
        {'connection': connection}
    )


# STAFF AND MANAGER: View all connection applications

@user_passes_test(staff_or_manager_required)

def staff_connection_list(request):

    status_filter = request.GET.get('status', '').strip()

    connections = WaterConnection.objects.select_related(
        'customer',
        'reviewed_by'
    ).all()

    valid_statuses = WaterConnection.Status.values

    if status_filter in valid_statuses:
        connections = connections.filter(status=status_filter)

    context = {
        'connections': connections,
        'status_filter': status_filter,

        'pending_count': WaterConnection.objects.filter(
            status=WaterConnection.Status.PENDING
        ).count(),

        'approved_count': WaterConnection.objects.filter(
            status=WaterConnection.Status.APPROVED
        ).count(),

        'rejected_count': WaterConnection.objects.filter(
            status=WaterConnection.Status.REJECTED
        ).count(),
    }

    return render(
        request,
        'customers/staff_connection_list.html',
        context
    )

# =====================================================
# STAFF AND MANAGER PERMISSION
# =====================================================

def staff_or_manager_required(user):
    return (
        user.is_authenticated
        and user.role in [
            CustomUser.Role.STAFF,
            CustomUser.Role.MANAGER
        ]
    )

# =====================================================
# STAFF AND MANAGER: VIEW CONNECTION APPLICATIONS
# =====================================================

@user_passes_test(staff_or_manager_required)
def staff_connection_list(request):

    status_filter = request.GET.get('status', '').strip()

    connections = WaterConnection.objects.select_related(
        'customer',
        'reviewed_by'
    ).all()

    valid_statuses = WaterConnection.Status.values

    if status_filter in valid_statuses:
        connections = connections.filter(status=status_filter)

    context = {
        'connections': connections,
        'status_filter': status_filter,

        'pending_count': WaterConnection.objects.filter(
            status=WaterConnection.Status.PENDING
        ).count(),

        'approved_count': WaterConnection.objects.filter(
            status=WaterConnection.Status.APPROVED
        ).count(),

        'rejected_count': WaterConnection.objects.filter(
            status=WaterConnection.Status.REJECTED
        ).count(),
    }

    return render(
        request,
        'customers/staff_connection_list.html',
        context
    )

# STAFF AND MANAGER: Review and approve/reject applications

@role_required(
    CustomUser.Role.STAFF,
    CustomUser.Role.MANAGER
)
def review_connection(request, connection_id):

    connection = get_object_or_404(
        WaterConnection.objects.select_related('customer'),
        id=connection_id
    )

    if request.method == 'POST':

        action = request.POST.get('action')
        remarks = request.POST.get('staff_remarks', '').strip()

        if connection.status != WaterConnection.Status.PENDING:
            messages.error(
                request,
                'This application has already been reviewed.'
            )
            return redirect('staff_connection_list')

        if action == 'approve':
            connection.approve(request.user)

            messages.success(
                request,
                f'Application approved. Connection number: '
                f'{connection.connection_number}'
            )

        elif action == 'reject':

            if not remarks:
                messages.error(
                    request,
                    'Please provide a reason before rejecting the application.'
                )

                return render(
                    request,
                    'customers/review_connection.html',
                    {'connection': connection}
                )

            connection.reject(request.user, remarks)

            messages.success(
                request,
                'Connection application rejected.'
            )

        else:
            messages.error(request, 'Invalid review action.')

        return redirect('staff_connection_list')

    return render(
        request,
        'customers/review_connection.html',
        {'connection': connection}
    )



# ------------------------------------------
# STAFF: VIEW APPROVED CONNECTIONS
# ------------------------------------------

@role_required(CustomUser.Role.STAFF)
def staff_reading_list(request):

    connections = WaterConnection.objects.filter(
        status=WaterConnection.Status.APPROVED
    ).select_related(
        'customer'
    ).order_by('-submitted_at')

    context = {
        'connections': connections,
    }

    return render(
        request,
        'customers/staff_reading_list.html',
        context
    )


# ------------------------------------------
# STAFF: RECORD A METER READING
# ------------------------------------------

@role_required(CustomUser.Role.STAFF)
def record_reading(request, connection_id):

    connection = get_object_or_404(
        WaterConnection,
        id=connection_id,
        status=WaterConnection.Status.APPROVED
    )

    latest_reading = MeterReading.objects.filter(
        connection=connection
    ).order_by('-reading_date', '-id').first()

    previous_reading = (
        latest_reading.current_reading
        if latest_reading
        else 0
    )

    reading_instance = MeterReading(
        connection=connection,
        recorded_by=request.user,
        previous_reading=previous_reading
    )

    if request.method == 'POST':

        form = MeterReadingForm(
            request.POST,
            instance=reading_instance
        )

        if form.is_valid():

            reading = form.save(commit=False)

            # Server-controlled values
            reading.connection = connection
            reading.recorded_by = request.user
            reading.previous_reading = previous_reading

            try:
                reading.full_clean()
                reading.save()

                messages.success(
                    request,
                    'Meter reading recorded successfully. '
                    f'Consumption: {reading.consumption} units.'
                )

                return redirect('staff_reading_list')

            except Exception as error:
                messages.error(request, str(error))

    else:

        form = MeterReadingForm(
            instance=reading_instance
        )

    context = {
        'form': form,
        'connection': connection,
        'previous_reading': previous_reading,
        'latest_reading': latest_reading,
    }

    return render(
        request,
        'customers/record_reading.html',
        context
    )


# ------------------------------------------
# CUSTOMER: VIEW OWN METER READING HISTORY
# ------------------------------------------

@role_required(CustomUser.Role.CUSTOMER)
def my_readings(request):

    readings = MeterReading.objects.filter(
        connection__customer=request.user
    ).select_related(
        'connection',
        'recorded_by'
    ).order_by(
        '-reading_date',
        '-id'
    )

    context = {
        'readings': readings,
    }

    return render(
        request,
        'customers/my_readings.html',
        context
    )


def staff_or_manager_required(user):
    return (
        user.is_authenticated
        and user.role in [
            CustomUser.Role.STAFF,
            CustomUser.Role.MANAGER
        ]
    )