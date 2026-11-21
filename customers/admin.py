
from django.contrib import admin
from .models import WaterConnection, MeterReading



@admin.register(WaterConnection)
class WaterConnectionAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'connection_number',
        'applicant_name',
        'customer',
        'connection_type',
        'status',
        'submitted_at',
    )

    list_filter = (
        'status',
        'connection_type',
    )

    search_fields = (
        'connection_number',
        'applicant_name',
        'customer__username',
        'contact_number',
    )

    readonly_fields = (
        'connection_number',
        'submitted_at',
        'reviewed_at',
        'reviewed_by',
    )





@admin.register(MeterReading)
class MeterReadingAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'connection',
        'previous_reading',
        'current_reading',
        'consumption',
        'reading_date',
        'recorded_by',
    )

    list_filter = (
        'reading_date',
    )

    search_fields = (
        'connection__connection_number',
        'connection__applicant_name',
        'recorded_by__username',
    )

    readonly_fields = (
        'consumption',
        'created_at',
    )
