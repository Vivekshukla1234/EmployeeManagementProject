from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db.models import Avg, Count
from employee.models import Employee
from employee.views import role_required
from attendance.models import Attendance
from leaveapp.models import LeaveRequest
from .models import PerformanceRecord
from .forms import PerformanceRecordForm
from .ml import predict_performance_grade
from datetime import date, timedelta
import calendar
import json

@role_required(['Admin'])
def admin_performance_list_view(request):
    q = request.GET.get('q', '')
    month_filter = request.GET.get('month', '')
    year_filter = request.GET.get('year', '')
    
    records = PerformanceRecord.objects.all()
    
    if q:
        from django.db.models import Q
        records = records.filter(
            Q(employee__name__icontains=q) |
            Q(employee__department__icontains=q)
        )
        
    if month_filter:
        records = records.filter(month=int(month_filter))
        
    if year_filter:
        records = records.filter(year=int(year_filter))
        
    today = date.today()
    month_choices = [(i, calendar.month_name[i]) for i in range(1, 13)]
    year_choices = list(range(today.year - 5, today.year + 2))
    
    return render(request, 'analytics/performance_list.html', {
        'records': records,
        'search_query': q,
        'selected_month': month_filter,
        'selected_year': year_filter,
        'month_choices': month_choices,
        'year_choices': year_choices,
    })

@role_required(['Admin'])
def admin_performance_create_edit_view(request, pk=None):
    if pk:
        record = get_object_or_404(PerformanceRecord, pk=pk)
        title = "Edit Performance Record"
    else:
        record = None
        title = "Record New Performance Entry"
        
    if request.method == 'POST':
        form = PerformanceRecordForm(request.POST, instance=record)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Performance record saved successfully.")
                return redirect('admin_performance_list')
            except Exception as e:
                # Handle unique constraint violation (e.g. employee + month + year already exists)
                form.add_error(None, "A performance record already exists for this employee for the selected month/year.")
    else:
        form = PerformanceRecordForm(instance=record)
        
    return render(request, 'analytics/performance_form.html', {
        'form': form,
        'title': title,
        'record': record
    })

@role_required(['Admin'])
def admin_performance_delete_view(request, pk):
    if request.method == 'POST':
        record = get_object_or_404(PerformanceRecord, pk=pk)
        record.delete()
        messages.success(request, "Performance record deleted successfully.")
    return redirect('admin_performance_list')

@login_required
def employee_performance_history_view(request):
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        if request.user.is_superuser:
            return redirect('admin_performance_list')
        messages.error(request, "Employee profile not found.")
        return redirect('dashboard')
        
    if employee.role == 'Admin':
        return redirect('admin_performance_list')
        
    records = PerformanceRecord.objects.filter(employee=employee).order_by('-year', '-month')
    
    return render(request, 'analytics/performance_history.html', {
        'records': records,
        'employee': employee,
    })

@role_required(['Admin'])
def admin_ai_predict_view(request):
    prediction = None
    attendance = None
    task_completion = None
    rating = None
    
    if request.method == 'POST':
        attendance_str = request.POST.get('attendance')
        task_completion_str = request.POST.get('task_completion')
        rating_str = request.POST.get('rating')
        
        try:
            attendance = float(attendance_str)
            task_completion = float(task_completion_str)
            rating = float(rating_str)
            
            if not (0.0 <= attendance <= 100.0) or not (0.0 <= task_completion <= 100.0) or not (0.0 <= rating <= 5.0):
                raise ValueError("Values outside of range constraints.")
                
            prediction = predict_performance_grade(attendance, task_completion, rating)
            
        except (ValueError, TypeError):
            messages.error(request, "Please provide valid numeric inputs within range constraints (Attendance 0-100, Task 0-100, Rating 0-5).")
            
    return render(request, 'analytics/ai_predict.html', {
        'prediction': prediction,
        'attendance': attendance,
        'task_completion': task_completion,
        'rating': rating,
    })

@role_required(['Admin'])
def admin_analytics_dashboard_view(request):
    # Summary Cards
    total_employees = Employee.objects.count()
    
    # Calculate average attendance % overall
    avg_attendance = PerformanceRecord.objects.aggregate(Avg('attendance_percentage'))['attendance_percentage__avg'] or 0.0
    pending_leaves = LeaveRequest.objects.filter(status='Pending').count()
    evaluated_scores = PerformanceRecord.objects.count()
    
    # Chart 1: Employee Count by Department
    dept_data = Employee.objects.values('department').annotate(count=Count('id'))
    dept_labels = [d['department'] for d in dept_data]
    dept_counts = [d['count'] for d in dept_data]
    
    # Chart 2: Attendance Trend (last 15 days check-ins)
    today = date.today()
    trend_dates = []
    trend_counts = []
    for i in range(14, -1, -1):
        target_date = today - timedelta(days=i)
        trend_dates.append(target_date.strftime('%b %d'))
        check_ins = Attendance.objects.filter(date=target_date, status='Present').count()
        trend_counts.append(check_ins)
        
    # Chart 3: Performance Distribution (AI grades counts)
    grade_counts = {'Excellent': 0, 'Good': 0, 'Average': 0, 'Poor': 0}
    db_grades = PerformanceRecord.objects.values('ai_grade').annotate(count=Count('id'))
    for item in db_grades:
        grade = item['ai_grade']
        if grade in grade_counts:
            grade_counts[grade] = item['count']
            
    grade_labels = list(grade_counts.keys())
    grade_data = list(grade_counts.values())
    
    context = {
        'total_employees': total_employees,
        'avg_attendance': avg_attendance,
        'pending_leaves': pending_leaves,
        'evaluated_scores': evaluated_scores,
        
        # Serialize to JSON strings for frontend Chart.js parsing
        'dept_labels_json': json.dumps(dept_labels),
        'dept_counts_json': json.dumps(dept_counts),
        'trend_dates_json': json.dumps(trend_dates),
        'trend_counts_json': json.dumps(trend_counts),
        'grade_labels_json': json.dumps(grade_labels),
        'grade_data_json': json.dumps(grade_data),
    }
    
    return render(request, 'analytics/dashboard.html', context)
