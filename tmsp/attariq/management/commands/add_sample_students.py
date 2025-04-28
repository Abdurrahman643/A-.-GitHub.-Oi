from django.core.management.base import BaseCommand
from attariq.models import Student

class Command(BaseCommand):
    help = 'Add sample Student data for testing'

    def handle(self, *args, **kwargs):
        sample_students = [
            {
                'full_name': 'John Doe',
                'email': 'john.doe@example.com',
                'phone': '1234567890',
                'address': '123 Main St',
                'is_tahfeez': False,
                'school_section': 'Primary',
                'tahfeez_section': None,
            },
            {
                'full_name': 'Jane Smith',
                'email': 'jane.smith@example.com',
                'phone': '0987654321',
                'address': '456 Elm St',
                'is_tahfeez': True,
                'school_section': 'Junior School',
                'tahfeez_section': 'Weekdays',
            },
        ]

        for student_data in sample_students:
            student, created = Student.objects.get_or_create(
                full_name=student_data['full_name'],
                defaults=student_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created student: {student.full_name}"))
            else:
                self.stdout.write(f"Student already exists: {student.full_name}")
