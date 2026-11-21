
from django.urls import path
from . import views

urlpatterns = [

    # Customer URLs
    path(
        'complaints/submit/',
        views.submit_complaint,
        name='submit_complaint'
    ),

    path(
        'my-complaints/',
        views.my_complaints,
        name='my_complaints'
    ),

    # Complaint detail
    path(
        'complaints/<int:complaint_id>/',
        views.complaint_detail,
        name='complaint_detail'
    ),

    # Staff and Manager URLs
    path(
        'staff/complaints/',
        views.staff_complaint_list,
        name='staff_complaint_list'
    ),

    path(
        'staff/complaints/<int:complaint_id>/update/',
        views.update_complaint,
        name='update_complaint'
    ),

]
