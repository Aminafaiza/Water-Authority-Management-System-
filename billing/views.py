
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST

from accounts.models import CustomUser
from accounts.decorators import role_required

from customers.models import MeterReading
from .models import Bill
from .services import generate_bill_for_reading
from django.db import IntegrityError
from django.http import HttpResponseForbidden

from .forms import PaymentSubmissionForm
from .models import Payment
from .payment_services import verify_payment, reject_payment
from .forms import PaymentSubmissionForm, TariffForm
from .models import Tariff
# =====================================================
# STAFF: BILLING DASHBOARD
# =====================================================

@role_required(CustomUser.Role.STAFF)
def staff_bill_list(request):

    # Meter readings that do not have bills yet.
    unbilled_readings = MeterReading.objects.filter(
        connection__status='APPROVED',
        bill__isnull=True
    ).select_related(
        'connection',
        'connection__customer'
    ).order_by('-reading_date')

    # All generated bills.
    bills = Bill.objects.select_related(
        'connection',
        'connection__customer',
        'meter_reading'
    ).order_by('-generated_at')

    context = {
        'unbilled_readings': unbilled_readings,
        'bills': bills,

        'total_bills': bills.count(),

        'pending_bills': bills.filter(
            status=Bill.Status.PENDING
        ).count(),

        'paid_bills': bills.filter(
            status=Bill.Status.PAID
        ).count(),

        'overdue_bills': bills.filter(
            status=Bill.Status.OVERDUE
        ).count(),
    }

    return render(
        request,
        'billing/staff_bill_list.html',
        context
    )


# =====================================================
# STAFF: GENERATE BILL
# =====================================================

@role_required(CustomUser.Role.STAFF)
@require_POST
def generate_bill(request, reading_id):

    reading = get_object_or_404(
        MeterReading.objects.select_related('connection'),
        id=reading_id
    )

    try:

        bill, created = generate_bill_for_reading(
            reading,
            request.user
        )

        if created:
            messages.success(
                request,
                f'Bill {bill.bill_number} generated successfully.'
            )
        else:
            messages.warning(
                request,
                f'Bill {bill.bill_number} already exists for this reading.'
            )

    except ValueError as error:

        messages.error(request, str(error))

    return redirect('staff_bill_list')


# =====================================================
# CUSTOMER: MY BILLS
# =====================================================

@role_required(CustomUser.Role.CUSTOMER)
def my_bills(request):

    bills = Bill.objects.filter(
        connection__customer=request.user
    ).select_related(
        'connection',
        'meter_reading'
    ).order_by('-generated_at')

    context = {
        'bills': bills,

        'total_bills': bills.count(),

        'pending_bills': bills.filter(
            status=Bill.Status.PENDING
        ).count(),

        'paid_bills': bills.filter(
            status=Bill.Status.PAID
        ).count(),

        'overdue_bills': bills.filter(
            status=Bill.Status.OVERDUE
        ).count(),
    }

    return render(
        request,
        'billing/my_bills.html',
        context
    )


# =====================================================
# CUSTOMER / STAFF: BILL DETAILS
# =====================================================

@login_required
def bill_detail(request, bill_id):

    if request.user.role == CustomUser.Role.STAFF:

        bill = get_object_or_404(
            Bill.objects.select_related(
                'connection',
                'connection__customer',
                'meter_reading'
            ),
            id=bill_id
        )

    elif request.user.role == CustomUser.Role.CUSTOMER:

        bill = get_object_or_404(
            Bill.objects.select_related(
                'connection',
                'meter_reading'
            ),
            id=bill_id,
            connection__customer=request.user
        )

    else:
        raise PermissionDenied(
            'You do not have permission to view this bill.'
        )

    return render(
        request,
        'billing/bill_detail.html',
        {'bill': bill}
    )



# =====================================================
# CUSTOMER: SUBMIT PAYMENT
# =====================================================

@role_required(CustomUser.Role.CUSTOMER)
def submit_payment(request, bill_id):

    bill = get_object_or_404(
        Bill,
        id=bill_id,
        connection__customer=request.user
    )

    # Do not accept another payment if bill is paid.
    if bill.status == Bill.Status.PAID:
        messages.info(
            request,
            'This bill has already been paid.'
        )
        return redirect('my_bills')

    # Do not allow another pending attempt for the same bill.
    pending_payment = Payment.objects.filter(
        bill=bill,
        status=Payment.Status.PENDING
    ).exists()

    if pending_payment:
        messages.warning(
            request,
            'A payment submission for this bill is already awaiting verification.'
        )
        return redirect('payment_history')

    if request.method == 'POST':

        form = PaymentSubmissionForm(request.POST)

        if form.is_valid():

            payment = form.save(commit=False)

            # Server-controlled fields
            payment.bill = bill
            payment.customer = request.user
            payment.amount = bill.total_amount
            payment.status = Payment.Status.PENDING

            try:
                payment.save()

                payment.payment_number = f'ACP-{payment.pk:06d}'

                payment.save(
                    update_fields=['payment_number']
                )

                messages.success(
                    request,
                    'Payment details submitted successfully. '
                    'Your payment is waiting for staff verification.'
                )

                return redirect('payment_history')

            except IntegrityError:

                messages.error(
                    request,
                    'This transaction reference has already been submitted.'
                )

    else:
        form = PaymentSubmissionForm()

    return render(
        request,
        'billing/submit_payment.html',
        {
            'bill': bill,
            'form': form,
        }
    )


# =====================================================
# CUSTOMER: PAYMENT HISTORY
# =====================================================

@role_required(CustomUser.Role.CUSTOMER)
def payment_history(request):

    payments = Payment.objects.filter(
        customer=request.user
    ).select_related(
        'bill',
        'bill__connection'
    ).order_by('-created_at')

    context = {
        'payments': payments,

        'total_payments': payments.count(),

        'pending_payments': payments.filter(
            status=Payment.Status.PENDING
        ).count(),

        'verified_payments': payments.filter(
            status=Payment.Status.VERIFIED
        ).count(),

        'rejected_payments': payments.filter(
            status=Payment.Status.REJECTED
        ).count(),
    }

    return render(
        request,
        'billing/payment_history.html',
        context
    )


# =====================================================
# STAFF: PAYMENT MANAGEMENT
# =====================================================

@role_required(CustomUser.Role.STAFF)
def staff_payment_list(request):

    payments = Payment.objects.select_related(
        'bill',
        'customer',
        'bill__connection'
    ).order_by('-created_at')

    context = {
        'payments': payments,

        'total_payments': payments.count(),

        'pending_payments': payments.filter(
            status=Payment.Status.PENDING
        ).count(),

        'verified_payments': payments.filter(
            status=Payment.Status.VERIFIED
        ).count(),

        'rejected_payments': payments.filter(
            status=Payment.Status.REJECTED
        ).count(),
    }

    return render(
        request,
        'billing/staff_payment_list.html',
        context
    )


# =====================================================
# STAFF: VERIFY PAYMENT
# =====================================================

@role_required(CustomUser.Role.STAFF)
@require_POST
def payment_verify(request, payment_id):

    payment = get_object_or_404(
        Payment,
        id=payment_id
    )

    try:

        payment = verify_payment(
            payment.id,
            request.user
        )

        messages.success(
            request,
            f'Payment {payment.payment_number} verified successfully. '
            'The bill is now marked as paid.'
        )

    except (ValueError, IntegrityError) as error:

        messages.error(
            request,
            str(error) or 'Unable to verify this payment.'
        )

    return redirect('staff_payment_list')


# =====================================================
# STAFF: REJECT PAYMENT
# =====================================================

@role_required(CustomUser.Role.STAFF)
@require_POST
def payment_reject(request, payment_id):

    payment = get_object_or_404(
        Payment,
        id=payment_id
    )

    remarks = request.POST.get(
        'staff_remarks',
        ''
    ).strip()

    try:

        reject_payment(
            payment.id,
            request.user,
            remarks
        )

        messages.success(
            request,
            'Payment rejected successfully.'
        )

    except ValueError as error:

        messages.error(
            request,
            str(error)
        )

    return redirect('staff_payment_list')


# =====================================================
# CUSTOMER: PAYMENT RECEIPT
# =====================================================

@role_required(CustomUser.Role.CUSTOMER)
def payment_receipt(request, payment_id):

    payment = get_object_or_404(
        Payment.objects.select_related(
            'bill',
            'bill__connection'
        ),
        id=payment_id,
        customer=request.user,
        status=Payment.Status.VERIFIED
    )

    return render(
        request,
        'billing/payment_receipt.html',
        {'payment': payment}
    )


# =====================================================
# MANAGER: DYNAMIC TARIFF MANAGEMENT
# =====================================================

@role_required(CustomUser.Role.MANAGER)
def tariff_management(request):

    tariffs = Tariff.objects.all()

    # Check whether the manager selected an existing tariff to edit.
    edit_id = request.GET.get('edit')

    if edit_id:
        tariff_instance = get_object_or_404(
            Tariff,
            id=edit_id
        )
    else:
        tariff_instance = None

    if request.method == 'POST':

        # If tariff_id exists, update that tariff.
        # Otherwise, create a new tariff.
        tariff_id = request.POST.get('tariff_id')

        if tariff_id:
            tariff_instance = get_object_or_404(
                Tariff,
                id=tariff_id
            )
        else:
            tariff_instance = None

        form = TariffForm(
            request.POST,
            instance=tariff_instance
        )

        if form.is_valid():

            tariff = form.save(commit=False)

            # Record the manager who updated the tariff.
            tariff.updated_by = request.user

            tariff.save()

            messages.success(
                request,
                f'{tariff.get_connection_type_display()} tariff saved successfully.'
            )

            return redirect('tariff_management')

    else:

        form = TariffForm(
            instance=tariff_instance
        )

    context = {
        'tariffs': tariffs,
        'form': form,
        'editing_tariff': tariff_instance,
    }

    return render(
        request,
        'billing/tariff_management.html',
        context
    )