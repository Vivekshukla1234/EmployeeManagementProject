from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Employee

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create user and employee profile for Admin
        self.admin_user = User.objects.create_user(username='admin_user', password='password123', email='admin@example.com')
        self.admin_profile = Employee.objects.create(
            user=self.admin_user,
            name="Admin User",
            email="admin@example.com",
            phone="111-222-3333",
            department="IT",
            designation="Manager",
            salary=5000.0,
            role="Admin"
        )
        
        # Create user and employee profile for normal Employee
        self.employee_user = User.objects.create_user(username='employee_user', password='password123', email='employee@example.com')
        self.employee_profile = Employee.objects.create(
            user=self.employee_user,
            name="Employee User",
            email="employee@example.com",
            phone="444-555-6666",
            department="Sales",
            designation="Representative",
            salary=2500.0,
            role="Employee"
        )

    def test_login_url_status(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')

    def test_admin_login_redirect(self):
        response = self.client.post(reverse('login'), {
            'username': 'admin_user',
            'password': 'password123',
            'role': 'Admin'
        })
        self.assertRedirects(response, reverse('dashboard'), target_status_code=302)
        
        # Check that going to dashboard redirect sends admin to admin-dashboard
        response_dash = self.client.get(reverse('dashboard'))
        self.assertRedirects(response_dash, reverse('admin_dashboard'))

    def test_employee_login_redirect(self):
        response = self.client.post(reverse('login'), {
            'username': 'employee_user',
            'password': 'password123',
            'role': 'Employee'
        })
        self.assertRedirects(response, reverse('dashboard'), target_status_code=302)
        
        # Check that going to dashboard redirect sends employee to employee-dashboard
        response_dash = self.client.get(reverse('dashboard'))
        self.assertRedirects(response_dash, reverse('employee_dashboard'))

    def test_role_mismatch_login_fails(self):
        # Admin trying to log in as Employee
        response = self.client.post(reverse('login'), {
            'username': 'admin_user',
            'password': 'password123',
            'role': 'Employee'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid login role selection")

    def test_unauthorized_admin_access_by_employee(self):
        # Log in as normal employee
        self.client.login(username='employee_user', password='password123')
        
        # Try to access admin dashboard (should redirect to employee dashboard)
        response = self.client.get(reverse('admin_dashboard'))
        self.assertRedirects(response, reverse('employee_dashboard'))

    def test_unauthorized_employee_access_by_admin(self):
        # Log in as Admin
        self.client.login(username='admin_user', password='password123')
        
        # Try to access employee dashboard (should redirect to admin dashboard)
        response = self.client.get(reverse('employee_dashboard'))
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_password_reset_views_load(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        
        response_done = self.client.get(reverse('password_reset_done'))
        self.assertEqual(response_done.status_code, 200)
        
        response_complete = self.client.get(reverse('password_reset_complete'))
        self.assertEqual(response_complete.status_code, 200)


class EmployeeManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Admin User
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
        
        # Normal Employee 1
        self.emp_user1 = User.objects.create_user(username='emp1', password='password123')
        self.emp_profile1 = Employee.objects.create(
            user=self.emp_user1,
            name="Alice Smith",
            email="alice@company.com",
            phone="222",
            department="Engineering",
            designation="Developer",
            salary=5000.0,
            role="Employee"
        )

        # Normal Employee 2
        self.emp_user2 = User.objects.create_user(username='emp2', password='password123')
        self.emp_profile2 = Employee.objects.create(
            user=self.emp_user2,
            name="Bob Jones",
            email="bob@company.com",
            phone="333",
            department="Sales",
            designation="Representative",
            salary=4000.0,
            role="Employee"
        )

    def test_admin_can_add_employee(self):
        self.client.login(username='admin_user', password='password123')
        response = self.client.post(reverse('employee_add'), {
            'username': 'new_dev',
            'password': 'password123',
            'name': 'New Developer',
            'email': 'new_dev@company.com',
            'phone': '444',
            'department': 'Engineering',
            'designation': 'Junior Developer',
            'salary': 3000.0,
            'role': 'Employee'
        })
        self.assertRedirects(response, reverse('admin_dashboard'))
        
        # Verify creation in DB
        user_exists = User.objects.filter(username='new_dev').exists()
        self.assertTrue(user_exists)
        emp_exists = Employee.objects.filter(email='new_dev@company.com').exists()
        self.assertTrue(emp_exists)
        
        new_emp = Employee.objects.get(email='new_dev@company.com')
        self.assertEqual(new_emp.user.username, 'new_dev')

    def test_employee_cannot_add_employee(self):
        self.client.login(username='emp1', password='password123')
        response = self.client.post(reverse('employee_add'), {
            'username': 'new_dev',
            'password': 'password123',
            'name': 'New Developer',
            'email': 'new_dev@company.com',
            'phone': '444',
            'role': 'Employee'
        })
        # Normal employee is redirected to their own dashboard
        self.assertRedirects(response, reverse('employee_dashboard'))
        
        # Verify not created in DB
        self.assertFalse(User.objects.filter(username='new_dev').exists())

    def test_admin_can_edit_employee(self):
        self.client.login(username='admin_user', password='password123')
        response = self.client.post(reverse('employee_edit', kwargs={'pk': self.emp_profile1.pk}), {
            'name': 'Alice Smith Updated',
            'email': 'alice_new@company.com',
            'phone': '222-Updated',
            'department': 'Product',
            'designation': 'Tech Lead',
            'salary': 6500.0,
            'role': 'Employee'
        })
        self.assertRedirects(response, reverse('admin_dashboard'))
        
        # Verify db updates
        updated_emp = Employee.objects.get(pk=self.emp_profile1.pk)
        self.assertEqual(updated_emp.name, 'Alice Smith Updated')
        self.assertEqual(updated_emp.phone, '222-Updated')
        self.assertEqual(updated_emp.department, 'Product')
        self.assertEqual(updated_emp.designation, 'Tech Lead')
        self.assertEqual(updated_emp.salary, 6500.0)
        # Sync validation
        self.assertEqual(updated_emp.user.email, 'alice_new@company.com')

    def test_admin_can_delete_employee(self):
        self.client.login(username='admin_user', password='password123')
        
        pk_to_delete = self.emp_profile2.pk
        user_id_to_delete = self.emp_user2.id
        
        response = self.client.post(reverse('employee_delete', kwargs={'pk': pk_to_delete}))
        self.assertRedirects(response, reverse('admin_dashboard'))
        
        # Verify deletions
        self.assertFalse(Employee.objects.filter(pk=pk_to_delete).exists())
        self.assertFalse(User.objects.filter(id=user_id_to_delete).exists())

    def test_profile_detail_view_permissions(self):
        # 1. Owner can access their own profile
        self.client.login(username='emp1', password='password123')
        response = self.client.get(reverse('employee_detail', kwargs={'pk': self.emp_profile1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice Smith")

        # 2. Owner cannot access another employee profile
        response = self.client.get(reverse('employee_detail', kwargs={'pk': self.emp_profile2.pk}))
        self.assertEqual(response.status_code, 403) # raises PermissionDenied

        # 3. Admin can access any profile
        self.client.login(username='admin_user', password='password123')
        response = self.client.get(reverse('employee_detail', kwargs={'pk': self.emp_profile1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice Smith")
        
        response = self.client.get(reverse('employee_detail', kwargs={'pk': self.emp_profile2.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bob Jones")

    def test_search_employees(self):
        self.client.login(username='admin_user', password='password123')
        
        # Querying by department
        response = self.client.get(reverse('admin_dashboard') + '?q=Sales')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bob Jones")
        self.assertNotContains(response, "Alice Smith")

        # Querying by name
        response = self.client.get(reverse('admin_dashboard') + '?q=Alice')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice Smith")
        self.assertNotContains(response, "Bob Jones")

