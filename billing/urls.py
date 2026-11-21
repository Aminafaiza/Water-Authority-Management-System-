
from django.urls import path
from . import views

urlpatterns = [

    # Staff billing
    path(
        'staff/billing/',
        views.staff_bill_list,
        name='staff_bill_list'
    ),

    path(
        'staff/billing/generate/<int:reading_id>/',
        views.generate_bill,
        name='generate_bill'
    ),

    # Customer billing
    path(
        'my-bills/',
        views.my_bills,
        name='my_bills'
    ),

    # Bill details
    path(
        'billing/<int:bill_id>/',
        views.bill_detail,
        name='bill_detail'
    ),



    # ==================================
    # CUSTOMER PAYMENTS
    # ==================================

    path(
        'billing/<int:bill_id>/pay/',
        views.submit_payment,
        name='submit_payment'
    ),

    path(
        'my-payments/',
        views.payment_history,
        name='payment_history'
    ),

    path(
        'payment-receipt/<int:payment_id>/',
        views.payment_receipt,
        name='payment_receipt'
    ),

    # ==================================
    # STAFF PAYMENT MANAGEMENT
    # ==================================

    path(
        'staff/payments/',
        views.staff_payment_list,
        name='staff_payment_list'
    ),

    path(
        'staff/payments/<int:payment_id>/verify/',
        views.payment_verify,
        name='payment_verify'
    ),

    path(
        'staff/payments/<int:payment_id>/reject/',
        views.payment_reject,
        name='payment_reject'
    ),


    # ==================================
    # MANAGER: TARIFF MANAGEMENT
    # ==================================

    path(
        'manager/tariffs/',
        views.tariff_management,
        name='tariff_management'
    ),
]



