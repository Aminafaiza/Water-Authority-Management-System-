
from django.db import transaction
from django.utils import timezone

from .models import Payment, Bill


@transaction.atomic
def verify_payment(payment_id, staff_user):

    payment = Payment.objects.select_for_update().get(
        id=payment_id
    )

    bill = Bill.objects.select_for_update().get(
        id=payment.bill_id
    )

    if payment.status != Payment.Status.PENDING:
        raise ValueError(
            'Only pending payments can be verified.'
        )

    if bill.status == Bill.Status.PAID:
        raise ValueError(
            'This bill has already been paid.'
        )

    if payment.customer_id != bill.connection.customer_id:
        raise ValueError(
            'Payment customer does not match the bill owner.'
        )

    if payment.amount != bill.total_amount:
        raise ValueError(
            'Payment amount does not match the bill amount.'
        )

    # Mark payment as verified.
    payment.status = Payment.Status.VERIFIED
    payment.verified_by = staff_user
    payment.verified_at = timezone.now()

    if not payment.payment_number:
        payment.payment_number = f'ACP-{payment.pk:06d}'

    payment.save(
        update_fields=[
            'status',
            'verified_by',
            'verified_at',
            'payment_number',
        ]
    )

    # Update the bill.
    bill.status = Bill.Status.PAID

    bill.save(
        update_fields=['status']
    )

    return payment


@transaction.atomic
def reject_payment(payment_id, staff_user, remarks):

    payment = Payment.objects.select_for_update().get(
        id=payment_id
    )

    if payment.status != Payment.Status.PENDING:
        raise ValueError(
            'Only pending payments can be rejected.'
        )

    if not remarks.strip():
        raise ValueError(
            'Please provide a reason for rejection.'
        )

    payment.status = Payment.Status.REJECTED
    payment.verified_by = staff_user
    payment.verified_at = timezone.now()
    payment.staff_remarks = remarks.strip()

    payment.save(
        update_fields=[
            'status',
            'verified_by',
            'verified_at',
            'staff_remarks',
        ]
    )

    return payment
