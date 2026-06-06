from django.urls import path
from . import views

urlpatterns = [
    path('performance/', views.admin_performance_list_view, name='admin_performance_list'),
    path('performance/add/', views.admin_performance_create_edit_view, name='admin_performance_create'),
    path('performance/<int:pk>/edit/', views.admin_performance_create_edit_view, name='admin_performance_edit'),
    path('performance/<int:pk>/delete/', views.admin_performance_delete_view, name='admin_performance_delete'),
    path('performance/my-history/', views.employee_performance_history_view, name='employee_performance_history'),
    path('performance/predict/', views.admin_ai_predict_view, name='admin_ai_predict'),
    path('dashboard/', views.admin_analytics_dashboard_view, name='admin_analytics_dashboard'),
]
