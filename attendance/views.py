from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from employee.models import Employee
from employee.views import role_required
from .models import Attendance
from .forms import AttendanceForm
from datetime import date, timedelta
import calendar

def calculate_attendance_stats(employee, year, month):
    # Retrieve logs for selected month/year
    attendances = employee.attendances.filter(date__year=year, date__month=month)
    present_days = attendances.filter(status='Present').count()
    
    today = date.today()
    if today.year == year and today.month == month:
        end_date = today
    else:
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
        
    first_day = date(year, month, 1)
    
    # Calculate weekdays (Mon-Fri) in the range
    total_working_days = 0
    curr = first_day
    while curr <= end_date:
        if curr.weekday() < 5:  # 0 to 4 is Mon to Fri
            total_working_days += 1
        curr += timedelta(days=1)
        
    # Check division safety
    if total_working_days > 0:
        percentage = (present_days / total_working_days) * 100
    else:
        percentage = 100.0 if present_days > 0 or first_day.weekday() >= 5 else 0.0
        
    return {
        'present_days': present_days,
        'total_working_days': total_working_days,
        'attendance_percentage': percentage,
        'attendances_list': attendances.order_by('date')
    }

@login_required
def mark_attendance_view(request):
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, "Employee profile not found.")
        return redirect('dashboard')

    if employee.role == 'Admin':
        messages.error(request, "Administrators do not need to log daily attendance.")
        return redirect('dashboard')

    today = date.today()
    
    # Restrict to weekdays
    if today.weekday() >= 5:
        messages.error(request, "Attendance cannot be marked on weekends.")
        return redirect('dashboard')
        
    # Check duplicate
    exists = Attendance.objects.filter(employee=employee, date=today).exists()
    if exists:
        messages.warning(request, "You have already checked in for today.")
    else:
        Attendance.objects.create(employee=employee, date=today, status='Present')
        messages.success(request, "Check-in successful! Attendance logged as Present.")
        
    return redirect('dashboard')

@login_required
def employee_attendance_report_view(request):
    # Fetch target employee (default is current user's profile)
    emp_id = request.GET.get('employee_id')
    if emp_id:
        employee = get_object_or_404(Employee, pk=emp_id)
    else:
        try:
            employee = request.user.employee
        except Employee.DoesNotExist:
            raise PermissionDenied("You do not have an employee profile.")

    # Permissions enforcement
    try:
        current_employee = request.user.employee
    except Employee.DoesNotExist:
        if request.user.is_superuser:
            current_employee = None
        else:
            raise PermissionDenied("You do not have an employee profile.")

    if current_employee and current_employee.role != 'Admin' and employee.pk != current_employee.pk:
        raise PermissionDenied("Access Denied: You cannot view other employee attendance records.")

    # Determine selected month/year
    today = date.today()
    try:
        month = int(request.GET.get('month', today.month))
        year = int(request.GET.get('year', today.year))
        if not (1 <= month <= 12) or not (2000 <= year <= 2100):
            raise ValueError
    except ValueError:
        month = today.month
        year = today.year

    stats = calculate_attendance_stats(employee, year, month)
    
    # Generate choices for filter form
    month_choices = [(i, calendar.month_name[i]) for i in range(1, 13)]
    year_choices = list(range(today.year - 5, today.year + 1))
    
    context = {
        'employee': employee,
        'selected_month': month,
        'selected_year': year,
        'month_choices': month_choices,
        'year_choices': year_choices,
        'present_days': stats['present_days'],
        'total_working_days': stats['total_working_days'],
        'attendance_percentage': stats['attendance_percentage'],
        'attendances': stats['attendances_list'],
        'is_admin': current_employee.role == 'Admin' if current_employee else True,
    }
    return render(request, 'attendance/report.html', context)

@role_required(['Admin'])
def admin_attendance_report_view(request):
    today = date.today()
    
    # Filters
    try:
        month = int(request.GET.get('month', today.month))
        year = int(request.GET.get('year', today.year))
        if not (1 <= month <= 12) or not (2000 <= year <= 2100):
            raise ValueError
    except ValueError:
        month = today.month
        year = today.year
        
    q = request.GET.get('q', '')
    
    employees = Employee.objects.all()
    if q:
        from django.db.models import Q
        employees = employees.filter(
            Q(name__icontains=q) |
            Q(department__icontains=q) |
            Q(designation__icontains=q)
        )
        
    # Build statistics table data
    report_data = []
    for emp in employees:
        stats = calculate_attendance_stats(emp, year, month)
        report_data.append({
            'employee': emp,
            'present_days': stats['present_days'],
            'total_working_days': stats['total_working_days'],
            'attendance_percentage': stats['attendance_percentage'],
        })
        
    month_choices = [(i, calendar.month_name[i]) for i in range(1, 13)]
    year_choices = list(range(today.year - 5, today.year + 1))
    
    context = {
        'report_data': report_data,
        'selected_month': month,
        'selected_year': year,
        'month_choices': month_choices,
        'year_choices': year_choices,
        'search_query': q,
    }
    return render(request, 'attendance/admin_report.html', context)

@role_required(['Admin'])
def admin_attendance_create_edit_view(request, pk=None):
    if pk:
        attendance = get_object_or_404(Attendance, pk=pk)
        title = "Edit Attendance Entry"
    else:
        attendance = None
        title = "Record New Attendance Entry"
        
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Attendance record saved successfully.")
                return redirect('admin_attendance_report')
            except Exception as e:
                # Handle unique constraint validation error gracefully
                form.add_error(None, "An attendance record already exists for this employee on the selected date.")
    else:
        form = AttendanceForm(instance=attendance)
        
    return render(request, 'attendance/edit.html', {
        'form': form,
        'title': title,
        'attendance': attendance
    })
