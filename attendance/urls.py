from django.urls import path
from . import views

urlpatterns = [
    path('mark/', views.mark_attendance_view, name='mark_attendance'),
    path('report/', views.employee_attendance_report_view, name='employee_attendance_report'),
    path('admin-report/', views.admin_attendance_report_view, name='admin_attendance_report'),
    path('manage/add/', views.admin_attendance_create_edit_view, name='admin_attendance_create'),
    path('manage/<int:pk>/edit/', views.admin_attendance_create_edit_view, name='admin_attendance_edit'),
]
