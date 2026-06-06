from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Dashboards
    path('', views.dashboard_redirect_view, name='home'),
    path('dashboard/', views.dashboard_redirect_view, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('employee-dashboard/', views.employee_dashboard_view, name='employee_dashboard'),

    # Employee CRUD Management
    path('employee/add/', views.employee_add_view, name='employee_add'),
    path('employee/<int:pk>/', views.employee_detail_view, name='employee_detail'),
    path('employee/<int:pk>/edit/', views.employee_edit_view, name='employee_edit'),
    path('employee/<int:pk>/delete/', views.employee_delete_view, name='employee_delete'),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Password Reset
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt'
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    path('password-reset/complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]
