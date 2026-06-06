from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from employee.models import Employee
from attendance.models import Attendance
from leaveapp.models import LeaveRequest
from analytics.models import PerformanceRecord
from analytics.forms import PerformanceRecordForm
from analytics.ml import predict_performance_grade
from unittest.mock import patch
from datetime import date as original_date
import json

# Custom MockDate subclass to bypass Django isinstance check and MagicMock problems
class MockDate(original_date):
    _mocked_today = original_date(2026, 6, 10)

    @classmethod
    def today(cls):
        return cls._mocked_today

class AnalyticsTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create Admin
        self.admin_user = User.objects.create_user(username='admin_user', password='password123')
        self.admin_profile = Employee.objects.create(
            user=self.admin_user,
            name="Admin Manager",
            email="admin@company.com",
            phone="111",
            department="Management",
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
    @patch('analytics.views.date', MockDate)
    def test_performance_score_calculation(self):
        # We mock today to Wednesday, June 10, 2026.
        # Weekdays in June 2026 up to June 10:
        # June 1, 2, 3, 4, 5, 8, 9, 10. Total working weekdays = 8 days.
        MockDate._mocked_today = original_date(2026, 6, 10)

        # Create 4 Present attendance logs (4/8 = 50%)
        Attendance.objects.create(employee=self.emp_profile, date=original_date(2026, 6, 1), status='Present')
        Attendance.objects.create(employee=self.emp_profile, date=original_date(2026, 6, 2), status='Present')
        Attendance.objects.create(employee=self.emp_profile, date=original_date(2026, 6, 3), status='Present')
        Attendance.objects.create(employee=self.emp_profile, date=original_date(2026, 6, 4), status='Present')

        record = PerformanceRecord.objects.create(
            employee=self.emp_profile,
            year=2026,
            month=6,
            task_completion_percentage=80.0,
            project_rating=4.0
        )

        # 0.4 * 50% + 0.3 * 80% + 0.3 * 4.0 = 20.0 + 24.0 + 1.2 = 45.20
        self.assertAlmostEqual(record.attendance_percentage, 50.0)
        self.assertAlmostEqual(record.performance_score, 45.20)
        self.assertTrue(record.ai_grade in ['Excellent', 'Good', 'Average', 'Poor'])

    def test_performance_input_validations(self):
        # 1. Invalid Task Completion percentage (> 100)
        form = PerformanceRecordForm({
            'employee': self.emp_profile.pk,
            'year': 2026,
            'month': 6,
            'task_completion_percentage': 105.0,
            'project_rating': 4.0
        })
        self.assertFalse(form.is_valid())
        self.assertIn('task_completion_percentage', form.errors)

        # 2. Invalid Project Rating (> 5)
        form = PerformanceRecordForm({
            'employee': self.emp_profile.pk,
            'year': 2026,
            'month': 6,
            'task_completion_percentage': 90.0,
            'project_rating': 5.5
        })
        self.assertFalse(form.is_valid())
        self.assertIn('project_rating', form.errors)

    def test_ai_grade_prediction_logic(self):
        grade_ex = predict_performance_grade(95.0, 90.0, 4.8)
        self.assertEqual(grade_ex, 'Excellent')

        grade_pr = predict_performance_grade(55.0, 50.0, 2.5)
        self.assertEqual(grade_pr, 'Poor')

    @patch('employee.views.date', MockDate)
    @patch('attendance.views.date', MockDate)
    @patch('analytics.views.date', MockDate)
    def test_end_to_end_workflow_integration(self):
        # 1. Admin logs in and creates a new employee profile
        self.client.login(username='admin_user', password='password123')
        add_response = self.client.post(reverse('employee_add'), {
            'username': 'integration_emp',
            'password': 'password123',
            'name': 'Integration Employee',
            'email': 'integration@company.com',
            'phone': '999',
            'department': 'QA',
            'designation': 'QA Engineer',
            'salary': 4000.0,
            'role': 'Employee'
        })
        self.assertRedirects(add_response, reverse('admin_dashboard'))
        new_emp = Employee.objects.get(email='integration@company.com')

        # 2. Mock Date to a Wednesday (June 3, 2026) and let the new employee check in
        MockDate._mocked_today = original_date(2026, 6, 3)
        self.client.login(username='integration_emp', password='password123')
        checkin_response = self.client.post(reverse('mark_attendance'))
        self.assertRedirects(checkin_response, reverse('dashboard'), target_status_code=302)
        self.assertTrue(Attendance.objects.filter(employee=new_emp, date=original_date(2026, 6, 3), status='Present').exists())

        # 3. Employee applies for leave for June 4 to June 5, 2026
        leave_response = self.client.post(reverse('apply_leave'), {
            'start_date': '2026-06-04',
            'end_date': '2026-06-05',
            'reason': 'Family function'
        })
        self.assertRedirects(leave_response, reverse('leave_history'))
        leave_req = LeaveRequest.objects.get(employee=new_emp)

        # 4. Admin logs in and approves the leave request
        self.client.login(username='admin_user', password='password123')
        approve_response = self.client.post(reverse('approve_leave', kwargs={'pk': leave_req.pk}))
        self.assertRedirects(approve_response, reverse('admin_leave_list'))

        # Verify attendance entries updated/created for the leave weekdays (June 4, June 5)
        self.assertEqual(Attendance.objects.filter(employee=new_emp, status='Leave').count(), 2)

        # 5. Admin records performance details for the new employee for June 2026
        # Date is mocked to June 10, 2026. Working weekdays up to June 10 = 8 days.
        # Present: June 3 (1 day). Leave: June 4, 5. Total working: 8 days.
        # Calculated attendance percentage: (1 / 8) * 100 = 12.5%
        MockDate._mocked_today = original_date(2026, 6, 10)
        perf_response = self.client.post(reverse('admin_performance_create'), {
            'employee': new_emp.pk,
            'year': 2026,
            'month': 6,
            'task_completion_percentage': 60.0,
            'project_rating': 3.0
        })
        self.assertRedirects(perf_response, reverse('admin_performance_list'))
        
        perf_record = PerformanceRecord.objects.get(employee=new_emp, year=2026, month=6)
        self.assertEqual(perf_record.attendance_percentage, 12.5)
        
        # 6. Verify employee dashboard shows performance and leave history
        self.client.login(username='integration_emp', password='password123')
        emp_dash = self.client.get(reverse('employee_dashboard'))
        self.assertEqual(emp_dash.status_code, 200)
        self.assertContains(emp_dash, "Performance Insights")

        # 7. Verify admin analytics dashboard loads correctly and counts are populated
        self.client.login(username='admin_user', password='password123')
        analytics_dash = self.client.get(reverse('admin_analytics_dashboard'))
        self.assertEqual(analytics_dash.status_code, 200)
        self.assertContains(analytics_dash, "System Analytics Dashboard")
