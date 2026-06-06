from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db import transaction
from employee.models import Employee
from employee.views import role_required
from attendance.models import Attendance
from .models import LeaveRequest
from .forms import LeaveRequestForm
from datetime import date, timedelta

@login_required
def apply_leave_view(request):
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        if request.user.is_superuser:
            employee = Employee.objects.create(
                user=request.user,
                name="Super Admin",
                email=request.user.email or "admin@company.com",
                role="Admin",
                salary=0.0
            )
        else:
            messages.error(request, "Employee profile not found.")
            return redirect('dashboard')

    if employee.role == 'Admin':
        messages.error(request, "Administrators do not need to apply for leave.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, employee=employee)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.employee = employee
            leave_request.save()
            messages.success(request, "Leave request submitted successfully.")
            return redirect('leave_history')
    else:
        form = LeaveRequestForm(employee=employee)

    return render(request, 'leaveapp/apply.html', {'form': form})

@login_required
def leave_history_view(request):
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        if request.user.is_superuser:
            return redirect('admin_leave_list')
        messages.error(request, "Employee profile not found.")
        return redirect('dashboard')

    if employee.role == 'Admin':
        return redirect('admin_leave_list')

    requests = LeaveRequest.objects.filter(employee=employee).order_by('-created_at')
    return render(request, 'leaveapp/history.html', {'requests': requests, 'employee': employee})

@role_required(['Admin'])
def admin_leave_list_view(request):
    status_filter = request.GET.get('status', '')
    q = request.GET.get('q', '')

    requests = LeaveRequest.objects.all()

    if status_filter:
        requests = requests.filter(status=status_filter)

    if q:
        from django.db.models import Q
        requests = requests.filter(
            Q(employee__name__icontains=q) |
            Q(employee__department__icontains=q) |
            Q(reason__icontains=q)
        )

    status_choices = LeaveRequest.STATUS_CHOICES

    return render(request, 'leaveapp/admin_list.html', {
        'requests': requests,
        'status_choices': status_choices,
        'selected_status': status_filter,
        'search_query': q,
    })

@role_required(['Admin'])
def approve_leave_view(request, pk):
    if request.method != 'POST':
        return redirect('admin_leave_list')

    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    if leave_request.status != 'Pending':
        messages.error(request, "Only pending leave requests can be approved.")
        return redirect('admin_leave_list')

    with transaction.atomic():
        leave_request.status = 'Approved'
        leave_request.save()

        curr = leave_request.start_date
        while curr <= leave_request.end_date:
            if curr.weekday() < 5:  # Mon-Fri
                Attendance.objects.update_or_create(
                    employee=leave_request.employee,
                    date=curr,
                    defaults={'status': 'Leave'}
                )
            curr += timedelta(days=1)

    messages.success(request, f"Leave request for {leave_request.employee.name} approved successfully.")
    return redirect('admin_leave_list')

@role_required(['Admin'])
def reject_leave_view(request, pk):
    if request.method != 'POST':
        return redirect('admin_leave_list')

    leave_request = get_object_or_404(LeaveRequest, pk=pk)

    if leave_request.status != 'Pending':
        messages.error(request, "Only pending leave requests can be rejected.")
        return redirect('admin_leave_list')

    leave_request.status = 'Rejected'
    leave_request.save()

    messages.success(request, f"Leave request for {leave_request.employee.name} rejected.")
    return redirect('admin_leave_list')
