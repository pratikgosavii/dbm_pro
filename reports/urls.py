from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('sales/', views.sales_report, name='sales_report'),
    path('payments/', views.payment_report, name='payment_report'),
    path('salaries/', views.salary_report, name='salary_report'),
]
