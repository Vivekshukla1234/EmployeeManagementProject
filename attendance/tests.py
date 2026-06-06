from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from employee.models import Employee
from attendance.models import Attendance
from unittest.mock import patch
import datetime
from datetime import date as original_date

# Custom MockDate subclass to bypass Django isinstance check and MagicMock problems
class MockDate(original_date):
    _mocked_today = original_date(2026, 6, 3)

    @classmethod
    def today(cls):
        return cls._mocked_today

class AttendanceTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create Admin
        self.admin_user = User.objects.create_user(username='admin_user', password='password123')
        self.admin_profile = Employee.objects.create(
            user=self.admin_user,
            name="Admin Manager",
            email="admin@company.com",
            phone="111",
            department="HQ",
            designation="Manager",
            salary=9000.0,
            role="Admin"
        )
        
        # Create Employee
        self.emp_user = User.objects.create_user(username='emp_user', password='password123')
        self.emp_profile = Employee.objects.create(
            user=self.emp_user,
            name="Alice Smith",
            email="alice@company.com",
            phone="222",
            department="Engineering",
            designation="Developer",
            salary=5000.0,
            role="Employee"
        )

    @patch('employee.views.date', MockDate)
    @patch('attendance.views.date', MockDate)
    def test_employee_check_in_weekday(self):
        # Mock date to a Wednesday (June 3, 2026)
        MockDate._mocked_today = original_date(2026, 6, 3)

        self.client.login(username='emp_user', password='password123')
        response = self.client.post(reverse('mark_attendance'))
        self.assertRedirects(response, reverse('dashboard'), target_status_code=302)

        # Verify entry created in DB
        self.assertEqual(Attendance.objects.filter(employee=self.emp_profile, date=original_date(2026, 6, 3)).count(), 1)
        att = Attendance.objects.get(employee=self.emp_profile, date=original_date(2026, 6, 3))
        self.assertEqual(att.status, 'Present')

    @patch('employee.views.date', MockDate)
    @patch('attendance.views.date', MockDate)
    def test_employee_check_in_weekend_restricted(self):
        # Mock date to a Saturday (June 6, 2026)
        MockDate._mocked_today = original_date(2026, 6, 6)

        self.client.login(username='emp_user', password='password123')
        response = self.client.post(reverse('mark_attendance'))
        self.assertRedirects(response, reverse('dashboard'), target_status_code=302)

        # Verify no entry created in DB
        self.assertEqual(Attendance.objects.filter(employee=self.emp_profile, date=original_date(2026, 6, 6)).count(), 0)

    @patch('employee.views.date', MockDate)
    @patch('attendance.views.date', MockDate)
    def test_employee_double_check_in_prevented(self):
        # Mock date to a Wednesday (June 3, 2026)
        MockDate._mocked_today = original_date(2026, 6, 3)

        # Log check-in once
        Attendance.objects.create(employee=self.emp_profile, date=original_date(2026, 6, 3), status='Present')

        self.client.login(username='emp_user', password='password123')
        response = self.client.post(reverse('mark_attendance'))
        self.assertRedirects(response, reverse('dashboard'), target_status_code=302)

        # Verify only 1 entry exists in DB
        self.assertEqual(Attendance.objects.filter(employee=self.emp_profile, date=original_date(2026, 6, 3)).count(), 1)

    @patch('employee.views.date', MockDate)
    @patch('attendance.views.date', MockDate)
    def test_attendance_ratio_calculation(self):
        # Let's mock today to Wednesday, June 10, 2026.
        # Weekdays in June 2026 up to June 10:
        # June 1 (Mon), June 2 (Tue), June 3 (Wed), June 4 (Thu), June 5 (Fri)
        # June 8 (Mon), June 9 (Tue), June 10 (Wed)
        # Total working weekdays up to June 10 = 8 days.
        MockDate._mocked_today = original_date(2026, 6, 10)

        # Log 4 present days (out of 8 working weekdays)
        Attendance.objects.create(employee=self.emp_profile, date=original_date(2026, 6, 1), status='Present')
        Attendance.objects.create(employee=self.emp_profile, date=original_date(2026, 6, 2), status='Present')
        Attendance.objects.create(employee=self.emp_profile, date=original_date(2026, 6, 3), status='Present')
        Attendance.objects.create(employee=self.emp_profile, date=original_date(2026, 6, 4), status='Present')

        # Log in and load dashboard (which triggers calculations)
        self.client.login(username='emp_user', password='password123')
        response = self.client.get(reverse('employee_dashboard'))
        self.assertEqual(response.status_code, 200)

        # Expected ratio: (4 / 8) * 100 = 50.0%
        self.assertContains(response, "50.0%")
        self.assertContains(response, "4d")
        self.assertContains(response, "8d")

    def test_admin_access_master_report(self):
        self.client.login(username='admin_user', password='password123')
        response = self.client.get(reverse('admin_attendance_report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice Smith")

    def test_employee_locked_out_master_report(self):
        self.client.login(username='emp_user', password='password123')
        response = self.client.get(reverse('admin_attendance_report'))
        self.assertRedirects(response, reverse('employee_dashboard'))

    def test_admin_can_override_attendance(self):
        self.client.login(username='admin_user', password='password123')
        
        # Override attendance for Alice Smith on June 15, 2026 to Leave
        response = self.client.post(reverse('admin_attendance_create'), {
            'employee': self.emp_profile.pk,
            'date': '2026-06-15',
            'status': 'Leave'
        })
        self.assertRedirects(response, reverse('admin_attendance_report'))

        # Verify entry created in DB
        self.assertEqual(Attendance.objects.filter(employee=self.emp_profile, date=original_date(2026, 6, 15)).count(), 1)
        att = Attendance.objects.get(employee=self.emp_profile, date=original_date(2026, 6, 15))
        self.assertEqual(att.status, 'Leave')
