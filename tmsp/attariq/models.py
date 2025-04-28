from django.db import models

from django.utils.text import slugify

# Choices for sections
SCHOOL_SECTION_CHOICES = [
    ('Nursery', 'Nursery'),
    ('Primary', 'Primary'),
    ('Junior School', 'Junior School'),
]

TAHFEEZ_SECTION_CHOICES = [
    ('Weekdays', 'Weekdays'),
    ('Weekend', 'Weekend'),
    ('Both', 'Both'),
]

ENROLLMENT_STATUS = [
    ('Pending', 'Pending'),
    ('Confirmed', 'Confirmed'),
    ('Withdrawn', 'Withdrawn'),
]

# Student model
class Student(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    is_tahfeez = models.BooleanField(default=False)  # Whether student is in Tahfeez
    school_section = models.CharField(max_length=20, choices=SCHOOL_SECTION_CHOICES, blank=True, null=True)
    tahfeez_section = models.CharField(max_length=20, choices=TAHFEEZ_SECTION_CHOICES, blank=True, null=True)
    date_enrolled = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)  # Slug for SEO-friendly URLs

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.full_name)
            slug = base_slug
            num = 1
            while Student.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name

# Enrollment model
from django.core.mail import send_mail

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=ENROLLMENT_STATUS, default='Pending')
    academic_year = models.CharField(max_length=20, default="2024/2025")
    is_paid = models.BooleanField(default=False)  # Tracks if the student has paid
    payment_reference = models.CharField(max_length=100, blank=True, null=True)  # Paystack reference

    class Meta:
        unique_together = ('student', 'academic_year')

    def update_status(self, new_status):
        allowed_transitions = {
            'Pending': ['Confirmed', 'Withdrawn'],
            'Confirmed': ['Withdrawn'],
            'Withdrawn': [],
        }
        if new_status not in allowed_transitions[self.status]:
            raise ValueError(f"Invalid status transition from {self.status} to {new_status}")

        self.status = new_status
        self.save()

        # Send email notification
        subject = f"Enrollment Status Updated to {new_status}"
        message = f"Dear {self.student.full_name},\n\nYour enrollment status has been updated to {new_status}."
        recipient_list = [self.student.email]
        send_mail(subject, message, 'no-reply@attariqacademy.com', recipient_list)

    def __str__(self):
        return f"{self.student.full_name} - {self.status}"

# Payment model
class Payment(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    reference = models.CharField(max_length=100)  # Paystack reference
    date = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)  # Whether the payment has been verified by Paystack

    def __str__(self):
        return f"Payment by {self.enrollment.student.full_name} - {self.amount} - Verified: {self.verified}"

# Testimonial model for parent testimonials
class Testimonial(models.Model):
    parent_name = models.CharField(max_length=100)
    student_name = models.CharField(max_length=100)
    message = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial from {self.parent_name} about {self.student_name}"

# Announcement model
class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
