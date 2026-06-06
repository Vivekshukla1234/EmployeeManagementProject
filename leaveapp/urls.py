from django.urls import path
from . import views

urlpatterns = [
    path('apply/', views.apply_leave_view, name='apply_leave'),
    path('history/', views.leave_history_view, name='leave_history'),
    path('admin/requests/', views.admin_leave_list_view, name='admin_leave_list'),
    path('admin/approve/<int:pk>/', views.approve_leave_view, name='approve_leave'),
    path('admin/reject/<int:pk>/', views.reject_leave_view, name='reject_leave'),
]
