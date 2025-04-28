from django import forms
from .models import Student, Enrollment, Payment, Testimonial, Announcement

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = '__all__'

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        exclude = ['reference']  # Exclude reference field so it's not required in form submission

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
