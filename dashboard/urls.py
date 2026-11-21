
from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.home_view,
        name='home'
    ),

    path(
        'customer/dashboard/',
        views.customer_dashboard,
        name='customer_dashboard'
    ),

    path(
        'staff/dashboard/',
        views.staff_dashboard,
        name='staff_dashboard'
    ),

    path(
        'manager/dashboard/',
        views.manager_dashboard,
        name='manager_dashboard'
    ),

    # Staff Management URLs

    path(
        'manager/staff/',
        views.staff_list,
        name='staff_list'
    ),

    path(
        'manager/staff/create/',
        views.staff_create,
        name='staff_create'
    ),

    path(
        'manager/staff/<int:staff_id>/edit/',
        views.staff_update,
        name='staff_update'
    ),

    path(
        'manager/staff/<int:staff_id>/toggle-status/',
        views.staff_toggle_status,
        name='staff_toggle_status'
    ),



    # ==========================================
# WORK ASSIGNMENT URLS - PHASE 15
# ==========================================

path(
    'manager/assignments/',
    views.assignment_list,
    name='assignment_list'
),

path(
    'manager/assignments/create/',
    views.create_assignment,
    name='create_assignment'
),

path(
    'manager/assignments/<int:assignment_id>/edit/',
    views.edit_assignment,
    name='edit_assignment'
),

path(
    'staff/my-assignments/',
    views.my_assignments,
    name='my_assignments'
),

path(
    'staff/my-assignments/<int:assignment_id>/update/',
    views.update_my_assignment,
    name='update_my_assignment'
),
]
