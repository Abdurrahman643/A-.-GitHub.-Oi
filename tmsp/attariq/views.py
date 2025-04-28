from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib import messages
from django.contrib.auth import logout
from .models import Payment, Enrollment, Testimonial, Announcement
from .forms import PaymentForm, AnnouncementForm, StudentForm, EnrollmentForm
import requests
import uuid
from django.conf import settings
from django.urls import reverse
import logging
import json
import os

logger = logging.getLogger(__name__)

# Home page view
def homepage(request):
    announcements = Announcement.objects.order_by('-created_at')
    return render(request, 'home.html', {'announcements': announcements})

@login_required
def announcements_api(request):
    announcements = Announcement.objects.order_by('-created_at')[:10]
    data = {
        'announcements': [
            {
                'title': a.title,
                'content': a.content,
                'created_at': a.created_at.isoformat(),
            }
            for a in announcements
        ]
    }
    return JsonResponse(data)

def core(request):
    return render(request, 'core.html')

def about_updated(request):
    return render(request, 'about.html')

def core_page(request, slug):
    return HttpResponse(f"Slug: {slug}")

@login_required
def announcement_form_view(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Announcement submitted successfully.")
            return redirect('home')
    else:
        form = AnnouncementForm()
    return render(request, 'announcement_form.html', {'form': form})

@login_required
def student_form_view(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Student added successfully.")
            return redirect('enrollment_decision')
    else:
        form = StudentForm()
    return render(request, 'student_form.html', {'form': form})

@login_required
def enrollment_decision_view(request):
    if request.method == 'POST':
        decision = request.POST.get('decision')
        if decision == 'yes':
            return redirect('enrollment_form')
        else:
            logout(request)
            return redirect('login')
    return render(request, 'enrollment_decision.html')

@login_required
def enrollment_form_view(request):
    payment_reference = request.GET.get('payment_reference', '')
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Enrollment successful.")
            return redirect('login')
    else:
        initial_data = {}
        if payment_reference:
            initial_data['payment_reference'] = payment_reference
        form = EnrollmentForm(initial=initial_data)
    return render(request, 'enrollment_form.html', {'form': form})

@login_required
def update_enrollment_status(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        enrollment.status = new_status
        enrollment.save()
        messages.success(request, "Enrollment status updated successfully.")
        return redirect('enrollment_form')
    return render(request, 'update_enrollment_status.html', {'enrollment': enrollment})

@login_required
def Payment_form_view(request):
    if not hasattr(settings, 'PAYSTACK_SECRET_KEY') or not settings.PAYSTACK_SECRET_KEY:
        messages.error(request, "Payment gateway is not configured properly.")
        return redirect('payment')

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.reference = str(uuid.uuid4()).replace('-', '').upper()[:12]
            payment.save()

            headers = {
                "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json",
            }

            ngrok_url = os.getenv('NGROK_URL')
            if ngrok_url:
                callback_url = f"{ngrok_url}/payment/verify/"
            else:
                callback_url = request.build_absolute_uri('/payment/verify/')

            logger.info(f"Using callback URL: {callback_url}")

            data = {
                "email": payment.enrollment.student.email,
                "amount": int(payment.amount * 100),
                "reference": payment.reference,
                "callback_url": callback_url,
            }
            response = requests.post(
                "https://api.paystack.co/transaction/initialize",
                headers=headers,
                json=data,
            )
            logger.info(f"Paystack response status code: {response.status_code}")
            logger.info(f"Paystack response text: {response.text}")
            try:
                res_data = response.json()
                logger.info(f"Paystack response: {res_data}")
            except Exception as e:
                logger.error(f"Error parsing Paystack response: {e}")
                messages.error(request, "Error processing payment. Please try again.")
                return redirect('payment')

            if res_data.get("status") and res_data.get("data"):
                auth_url = res_data["data"]["authorization_url"]
                return redirect(auth_url)
            else:
                messages.error(request, "Payment initialization failed. Please try again.")
                return redirect('payment')
        else:
            # Form is invalid, log errors and render the form with errors
            logger.error(f"Payment form errors: {form.errors}")
            return render(request, 'Payment.html', {'form': form})
    else:
        form = PaymentForm()
    reference = str(uuid.uuid4()).replace('-', '').upper()[:12]
    return render(request, 'Payment.html', {'form': form, 'reference': reference})

@login_required
def payment_verify(request):
    reference = request.GET.get('reference') or request.GET.get('trxref')
    if not reference:
        messages.error(request, "No payment reference provided.")
        return redirect('payment')

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    try:
        response = requests.get(url, headers=headers)
        res_data = response.json()
        if res_data['status'] and res_data['data']['status'] == 'success':
            payment = Payment.objects.filter(reference=reference).first()
            if payment:
                payment.verified = True
                payment.save()
                messages.success(request, "Payment verified successfully.")
                return redirect('payment_success', payment_id=payment.id)
            else:
                messages.error(request, "Payment record not found.")
        else:
            messages.error(request, "Payment verification failed.")
    except requests.RequestException:
        messages.error(request, "Error verifying payment.")
    return redirect('payment')

@login_required
def payment_success(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    # Render a success message page with a link to download the PDF receipt
    return render(request, 'payment_success.html', {'payment': payment})

@login_required
def payment_receipt(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    return render(request, 'payment_receipt.html', {'payment': payment})

@login_required
def payment_receipt_pdf(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    template_path = 'payment_receipt.html'
    context = {'payment': payment}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="payment_receipt_{payment_id}.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors while generating the PDF <pre>' + html + '</pre>')
    return response
