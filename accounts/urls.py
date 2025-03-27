from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Employee management
    path('employee/create/', views.employee_create, name='employee_create'),
    
    # Employee categories
    path('employee-categories/', views.employee_category_list, name='employee_category_list'),
    path('employee-categories/create/', views.employee_category_create, name='employee_category_create'),
]
