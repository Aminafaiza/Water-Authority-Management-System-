
from django.urls import path
from . import views


urlpatterns = [
    # Customer URLs
    path(
        'connections/apply/',
        views.apply_connection,
        name='apply_connection'
    ),

    path(
        'my-connections/',
        views.my_connections,
        name='my_connections'
    ),

    path(
        'connections/<int:connection_id>/',
        views.connection_detail,
        name='connection_detail'
    ),

    # Staff URLs
    path(
        'staff/connections/',
        views.staff_connection_list,
        name='staff_connection_list'
    ),

    path(
        'staff/connections/<int:connection_id>/review/',
        views.review_connection,
        name='review_connection'
    ),

 # Phase 11 - Meter Readings
    path(
        'staff/meter-readings/',
        views.staff_reading_list,
        name='staff_reading_list'
    ),

    path(
        'staff/meter-readings/<int:connection_id>/record/',
        views.record_reading,
        name='record_reading'
    ),

    path(
        'my-readings/',
        views.my_readings,
        name='my_readings'
    ),
]



