
from datetime import timedelta
from decimal import Decimal

from django.db import transaction

from .models import Bill
from customers.models import MeterReading, WaterConnection


# Demonstration tariff rates.
# These are NOT official Kerala Water Authority rates.

TARIFFS = {
    'DOMESTIC': {
        'rate_per_unit': Decimal('5.00'),
        'fixed_charge': Decimal('50.00'),
    },

    'COMMERCIAL': {
        'rate_per_unit': Decimal('10.00'),
        'fixed_charge': Decimal('100.00'),
    },

    'INDUSTRIAL': {
        'rate_per_unit': Decimal('15.00'),
        'fixed_charge': Decimal('250.00'),
    },
}


@transaction.atomic
def generate_bill_for_reading(reading, staff_user):

    connection = reading.connection

    # Only approved connections can be billed.
    if connection.status != WaterConnection.Status.APPROVED:
        raise ValueError(
            'Bills can only be generated for approved connections.'
        )

    # Prevent duplicate bill generation.
    existing_bill = Bill.objects.filter(
        meter_reading=reading
    ).first()

    if existing_bill:
        return existing_bill, False

    # Get the tariff for this connection type.
    tariff = TARIFFS.get(connection.connection_type)

    if tariff is None:
        raise ValueError('Tariff configuration not found.')

    # Find the previous meter reading date.
    previous_record = MeterReading.objects.filter(
        connection=connection,
        reading_date__lt=reading.reading_date
    ).order_by('-reading_date', '-id').first()

    if previous_record:
        period_start = previous_record.reading_date
    elif connection.reviewed_at:
        period_start = connection.reviewed_at.date()
    else:
        period_start = reading.reading_date

    period_end = reading.reading_date

    # Create the bill.
    bill = Bill.objects.create(
        meter_reading=reading,
        connection=connection,

        billing_period_start=period_start,
        billing_period_end=period_end,

        consumption=reading.consumption,

        rate_per_unit=tariff['rate_per_unit'],
        fixed_charge=tariff['fixed_charge'],

        due_date=reading.reading_date + timedelta(days=15),

        generated_by=staff_user,
    )

    # Generate a readable unique bill number.
    bill.bill_number = f'ACB-{bill.pk:06d}'

    bill.save(update_fields=['bill_number'])

    return bill, True
