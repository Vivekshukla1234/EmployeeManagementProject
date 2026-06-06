from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from .models import Employee
from .forms import EmployeeLoginForm, EmployeeAddForm, EmployeeEditForm
from datetime import date
from attendance.models import Attendance

def role_required(allowed_roles):
    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            try:
                employee = request.user.employee
            except Employee.DoesNotExist:
                # If they are superuser, auto-create an Admin Employee profile
                if request.user.is_superuser:
                    employee = Employee.objects.create(
                        user=request.user,
                        name=request.user.get_full_name() or request.user.username,
                        email=request.user.email,
                        role='Admin',
                        phone='',
                        department='Administration',
                        designation='Administrator',
                        salary=0.0
                    )
                else:
                    raise PermissionDenied("You do not have an employee profile.")
            
            if employee.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                # Redirect to appropriate dashboard if logged in but trying to access the wrong dashboard
                if employee.role == 'Admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('employee_dashboard')
        return _wrapped_view
    return decorator

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    error_message = None
    if request.method == 'POST':
        form = EmployeeLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            role = form.cleaned_data.get('role')
            
            # Retrieve or create profile
            try:
                employee = user.employee
            except Employee.DoesNotExist:
                if user.is_superuser:
                    employee = Employee.objects.create(
                        user=user,
                        name=user.get_full_name() or user.username,
                        email=user.email,
                        role='Admin',
                        phone='',
                        department='Administration',
                        designation='Administrator',
                        salary=0.0
                    )
                else:
                    form.add_error(None, "No employee profile associated with this account.")
                    return render(request, 'auth/login.html', {'form': form})
            
            # Verify role match
            if employee.role != role:
                form.add_error(None, f"Invalid login role selection. This account is registered as: {employee.role}.")
            else:
                login(request, user)
                return redirect('dashboard')
    else:
        form = EmployeeLoginForm()
        
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_redirect_view(request):
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        if request.user.is_superuser:
            employee = Employee.objects.create(
                user=request.user,
                name=request.user.get_full_name() or request.user.username,
                email=request.user.email,
                role='Admin',
                phone='',
                department='Administration',
                designation='Administrator',
                salary=0.0
            )
        else:
            raise PermissionDenied("Employee profile does not exist.")
            
    if employee.role == 'Admin':
        return redirect('admin_dashboard')
    else:
        return redirect('employee_dashboard')

@role_required(['Admin'])
def admin_dashboard_view(request):
    q = request.GET.get('q', '')
    employees = Employee.objects.all()
    if q:
        employees = employees.filter(
            Q(name__icontains=q) |
            Q(department__icontains=q) |
            Q(designation__icontains=q) |
            Q(email__icontains=q)
        )
    context = {
        'employees': employees,
        'employee_count': employees.count(),
        'admin_name': request.user.employee.name,
        'search_query': q,
    }
    return render(request, 'dashboard_admin.html', context)

@role_required(['Employee'])
def employee_dashboard_view(request):
    from attendance.views import calculate_attendance_stats
    employee = request.user.employee
    today = date.today()
    
    # Today's check-in status
    try:
        today_attendance = Attendance.objects.get(employee=employee, date=today)
        has_checked_in = True
        today_status = today_attendance.status
    except Attendance.DoesNotExist:
        has_checked_in = False
        today_status = "Not Marked"
        
    is_weekend = today.weekday() >= 5
    
    # Monthly stats calculation
    stats = calculate_attendance_stats(employee, today.year, today.month)
    
    # Fetch latest performance record
    from analytics.models import PerformanceRecord
    latest_performance = PerformanceRecord.objects.filter(employee=employee).order_by('-year', '-month').first()
    
    context = {
        'employee': employee,
        'has_checked_in': has_checked_in,
        'today_status': today_status,
        'today_status_color': '#34d399' if has_checked_in else '#f59e0b',
        'is_weekend': is_weekend,
        'attendance_percentage': stats['attendance_percentage'],
        'present_days': stats['present_days'],
        'total_working_days': stats['total_working_days'],
        'latest_performance': latest_performance,
    }
    return render(request, 'dashboard_employee.html', context)

# CRUD Views for Admin

@role_required(['Admin'])
def employee_add_view(request):
    if request.method == 'POST':
        form = EmployeeAddForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')
            
            with transaction.atomic():
                user = User.objects.create_user(username=username, email=email, password=password)
                
                # Make them staff if Admin role is selected
                role = form.cleaned_data.get('role')
                if role == 'Admin':
                    user.is_staff = True
                    user.save()
                    
                employee = form.save(commit=False)
                employee.user = user
                employee.save()
                
            return redirect('admin_dashboard')
    else:
        form = EmployeeAddForm()
    return render(request, 'employee_add.html', {'form': form})

@role_required(['Admin'])
def employee_edit_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeEditForm(request.POST, instance=employee)
        if form.is_valid():
            with transaction.atomic():
                updated_employee = form.save()
                
                # Sync User object details
                user = updated_employee.user
                if user:
                    user.email = updated_employee.email
                    role = updated_employee.role
                    user.is_staff = (role == 'Admin')
                    user.save()
                    
            return redirect('admin_dashboard')
    else:
        form = EmployeeEditForm(instance=employee)
    return render(request, 'employee_edit.html', {'form': form, 'employee': employee})

@role_required(['Admin'])
def employee_delete_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    # Restrict deleting themselves
    if employee.user == request.user:
        return render(request, 'employee_confirm_delete.html', {
            'employee': employee,
            'error_message': "For security reasons, you cannot delete your own active administrator profile."
        })
        
    if request.method == 'POST':
        with transaction.atomic():
            user = employee.user
            employee.delete()
            if user:
                user.delete()
        return redirect('admin_dashboard')
        
    return render(request, 'employee_confirm_delete.html', {'employee': employee})

@login_required
def employee_detail_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    # Verify access permission
    try:
        current_employee = request.user.employee
    except Employee.DoesNotExist:
        if request.user.is_superuser:
            # Superusers always allowed
            return render(request, 'employee_detail.html', {'employee': employee, 'is_admin': True})
        raise PermissionDenied("You do not have an employee profile.")
        
    if current_employee.role != 'Admin' and current_employee.pk != employee.pk:
        raise PermissionDenied("Access Denied: You do not have permissions to view other employee files.")
        
    return render(request, 'employee_detail.html', {
        'employee': employee,
        'is_admin': current_employee.role == 'Admin'
    })
