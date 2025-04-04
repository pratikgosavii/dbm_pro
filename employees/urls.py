from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    # Employee management
    path('', views.employee_list, name='employee_list'),
    path('<int:pk>/', views.employee_detail, name='employee_detail'),
    
    # Attendance management
    path('attendance/', views.attendance_log, name='attendance_log'),
    path('attendance/calendar/', views.attendance_calendar, name='attendance_calendar'),
    path('punch-in/', views.punch_in, name='punch_in'),
    path('punch-out/', views.punch_out, name='punch_out'),
    
    # Leave management
    path('leaves/', views.leave_list, name='leave_list'),
    path('leaves/create/', views.leave_create, name='leave_create'),
    path('leaves/<int:pk>/', views.leave_detail, name='leave_detail'),
    path('leaves/<int:pk>/respond/', views.leave_respond, name='leave_respond'),
    path('leaves/<int:pk>/cancel/', views.leave_cancel, name='leave_cancel'),
    
    # Salary management
    path('salaries/', views.salary_list, name='salary_list'),
    path('salaries/create/', views.salary_create, name='salary_create'),
    path('salaries/<int:pk>/update/', views.salary_update, name='salary_update'),
    path('salaries/<int:pk>/calculate/', views.salary_calculate, name='salary_calculate'),
    
    # Task management
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/update/', views.task_update, name='task_update'),
    path('tasks/<int:pk>/complete/', views.task_complete, name='task_complete'),
]
