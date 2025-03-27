from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    # Employee management
    path('', views.employees_list, name='employees_list'),
    path('create/', views.employee_create, name='employee_create'),
    path('detail/<int:pk>/', views.employee_detail, name='employee_detail'),
    
    # Task management
    path('tasks/', views.tasks_list, name='tasks_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/update/<int:pk>/', views.task_update, name='task_update'),
    path('tasks/delete/<int:pk>/', views.task_delete, name='task_delete'),
    
    # Attendance management
    path('attendance/', views.attendance, name='attendance'),
    
    # Salary management
    path('salary/', views.salary_list, name='salary_list'),
    path('salary/create/', views.salary_create, name='salary_create'),
    path('salary/history/<int:employee_id>/', views.salary_history, name='salary_history'),
    path('salary/report/', views.salary_report, name='salary_report'),
]
