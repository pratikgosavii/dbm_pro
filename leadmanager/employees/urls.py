from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.employee_list, name='employee_list'),
    path('<int:pk>/', views.employee_detail, name='employee_detail'),
    path('create/', views.employee_create, name='employee_create'),
    path('<int:pk>/update/', views.employee_update, name='employee_update'),
    path('timesheet/', views.timesheet, name='timesheet'),
    path('timesheet/<int:employee_id>/', views.timesheet, name='employee_timesheet'),
    path('punch-in/', views.punch_in, name='punch_in'),
    path('punch-out/', views.punch_out, name='punch_out'),
    path('salary-report/', views.salary_report, name='salary_report'),
]
