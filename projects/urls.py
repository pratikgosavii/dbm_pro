from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # Client URLs
    path('clients/', views.clients_list, name='clients_list'),
    path('clients/create/', views.client_create, name='client_create'),
    path('clients/update/<int:pk>/', views.client_update, name='client_update'),
    path('clients/delete/<int:pk>/', views.client_delete, name='client_delete'),
    
    # Project URLs
    path('', views.projects_list, name='projects_list'),
    path('create/', views.project_create, name='project_create'),
    path('update/<int:pk>/', views.project_update, name='project_update'),
    path('delete/<int:pk>/', views.project_delete, name='project_delete'),
    path('detail/<int:pk>/', views.project_detail, name='project_detail'),
    
    # Payment URLs
    path('payments/', views.payments_list, name='payments_list'),
    path('payments/create/', views.payment_create, name='payment_create'),
    path('payments/update/<int:pk>/', views.payment_update, name='payment_update'),
    path('payments/delete/<int:pk>/', views.payment_delete, name='payment_delete'),
]
