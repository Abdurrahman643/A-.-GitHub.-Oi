from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.homepage, name="home"),
    path('home/', views.homepage, name='home'),

    # Core page
    path('core/', views.core, name="core"),

    # About page
    path('about/', views.about_updated, name='about'),

    # Admission page
    path('admission/', views.core, name='admission'),

    # Student form page
    path('student-form/', views.student_form_view, name='student_form'),

    # Enrollment decision page
    path('enrollment-decision/', views.enrollment_decision_view, name='enrollment_decision'),

    # Enrollment form page
    path('enrollment-form/', views.enrollment_form_view, name='enrollment_form'),

    # Update enrollment status page
    path('enrollment/<int:enrollment_id>/update-status/', views.update_enrollment_status, name='update_enrollment_status'),

    # Core page for slug-based dynamic pages
    path('core/<slug:slug>/', views.core_page, name='core_page'),

    # Payment form page
    path('payment/', views.Payment_form_view, name='payment'),

    # Payment verification page
    path('payment/verify/', views.payment_verify, name='payment_verify'),

    # Payment success page
    path('payment/success/<int:payment_id>/', views.payment_success, name='payment_success'),

    # Payment receipt page
    path('payment/receipt/<int:payment_id>/', views.payment_receipt, name='payment_receipt'),

    # Payment receipt PDF download
    path('payment/receipt/<int:payment_id>/pdf/', views.payment_receipt_pdf, name='payment_receipt_pdf'),

    # Testimonial form page
    path('announcement/', views.announcement_form_view, name='announcement'),

    # Announcements API endpoint
    path('api/announcements/', views.announcements_api, name='announcements_api'),
]
