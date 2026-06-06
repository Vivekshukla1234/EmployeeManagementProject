from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from employee.models import Employee
from attendance.models import Attendance
from leaveapp.models import LeaveRequest
from leaveapp.forms import LeaveRequestForm
from datetime import date, timedelta

class LeaveManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create Admin user & profile
        self.admin_user = User.objects.create_user(username='admin_user', password='password123')
        self.admin_profile = Employee.objects.create(
            user=self.admin_user,
            name="Admin User",
            email="admin@company.com",
            phone="111",
            department="Management",
            designation="HR Manager",
            salary=9000.0,
            role="Admin"
        )
        
        # Create normal Employee user & profile
        self.emp_user = User.objects.create_user(username='emp_user', password='password123')
        self.emp_profile = Employee.objects.create(
            user=self.emp_user,
            name="Employee User",
            email="employee@company.com",
            phone="222",
            department="Engineering",
            designation="Software Engineer",
            salary=5000.0,
            role="Employee"
        )

    def test_apply_leave_success(self):
        self.client.login(username='emp_user', password='password123')
        response = self.client.post(reverse('apply_leave'), {
            'start_date': '2026-06-10',
            'end_date': '2026-06-12',
            'reason': 'Medical checkup'
        })
        self.assertRedirects(response, reverse('leave_history'))
        
        # Verify LeaveRequest created
        self.assertEqual(LeaveRequest.objects.count(), 1)
        req = LeaveRequest.objects.first()
        self.assertEqual(req.employee, self.emp_profile)
        self.assertEqual(req.status, 'Pending')
        self.assertEqual(req.reason, 'Medical checkup')

    def test_apply_leave_invalid_dates(self):
        # start_date > end_date
        self.client.login(username='emp_user', password='password123')
        response = self.client.post(reverse('apply_leave'), {
            'start_date': '2026-06-12',
            'end_date': '2026-06-10',
            'reason': 'Should fail'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(LeaveRequest.objects.exists())
        self.assertFormError(response.context['form'], None, "Start date cannot be after end date.")

    def test_apply_leave_overlap(self):
        # Log a leave request already
        LeaveRequest.objects.create(
            employee=self.emp_profile,
            start_date=date(2026, 6, 10),
            end_date=date(2026, 6, 12),
            reason='Trip',
            status='Pending'
        )
        
        self.client.login(username='emp_user', password='password123')
        # Try overlapping dates
        response = self.client.post(reverse('apply_leave'), {
            'start_date': '2026-06-11',
            'end_date': '2026-06-14',
            'reason': 'Overlapping leave'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(LeaveRequest.objects.count(), 1) # Only first exists
        self.assertFormError(response.context['form'], None, "You have an overlapping leave request during this period.")

    def test_admin_approve_leave_creates_attendance(self):
        req = LeaveRequest.objects.create(
            employee=self.emp_profile,
            start_date=date(2026, 6, 10),  # Wed
            end_date=date(2026, 6, 12),    # Fri
            reason='Trip',
            status='Pending'
        )
        
        self.client.login(username='admin_user', password='password123')
        response = self.client.post(reverse('approve_leave', kwargs={'pk': req.pk}))
        self.assertRedirects(response, reverse('admin_leave_list'))
        
        req.refresh_from_db()
        self.assertEqual(req.status, 'Approved')
        
        # Weekday days are Wed (10), Thu (11), Fri (12). Total 3 days. All weekdays.
        self.assertEqual(Attendance.objects.filter(employee=self.emp_profile, status='Leave').count(), 3)

    def test_admin_approve_leave_skips_weekends(self):
        # June 13 (Sat), June 14 (Sun), June 15 (Mon)
        req = LeaveRequest.objects.create(
            employee=self.emp_profile,
            start_date=date(2026, 6, 13),
            end_date=date(2026, 6, 15),
            reason='Trip',
            status='Pending'
        )
        
        self.client.login(username='admin_user', password='password123')
        self.client.post(reverse('approve_leave', kwargs={'pk': req.pk}))
        
        # Only Monday should have Leave attendance entry
        self.assertEqual(Attendance.objects.filter(employee=self.emp_profile, status='Leave').count(), 1)
        self.assertTrue(Attendance.objects.filter(employee=self.emp_profile, date=date(2026, 6, 15), status='Leave').exists())
        self.assertFalse(Attendance.objects.filter(employee=self.emp_profile, date=date(2026, 6, 13)).exists())
        self.assertFalse(Attendance.objects.filter(employee=self.emp_profile, date=date(2026, 6, 14)).exists())

    def test_admin_reject_leave(self):
        req = LeaveRequest.objects.create(
            employee=self.emp_profile,
            start_date=date(2026, 6, 10),
            end_date=date(2026, 6, 12),
            reason='Trip',
            status='Pending'
        )
        
        self.client.login(username='admin_user', password='password123')
        response = self.client.post(reverse('reject_leave', kwargs={'pk': req.pk}))
        self.assertRedirects(response, reverse('admin_leave_list'))
        
        req.refresh_from_db()
        self.assertEqual(req.status, 'Rejected')
        self.assertEqual(Attendance.objects.filter(employee=self.emp_profile).count(), 0)

    def test_leave_view_permissions(self):
        # 1. Employees cannot access admin leave list
        self.client.login(username='emp_user', password='password123')
        response = self.client.get(reverse('admin_leave_list'))
        self.assertRedirects(response, reverse('employee_dashboard'))
        
        # 2. Admins cannot apply for leave (redirected or error)
        self.client.login(username='admin_user', password='password123')
        response = self.client.get(reverse('apply_leave'))
        self.assertRedirects(response, reverse('dashboard'), target_status_code=302)
