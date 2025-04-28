from django.contrib import admin

from .models import Student, Enrollment, Payment, Testimonial

admin.site.register(Student)
admin.site.register(Enrollment)
admin.site.register(Payment)
admin.site.register(Testimonial)