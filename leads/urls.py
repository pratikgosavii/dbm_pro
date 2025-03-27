from django.urls import path
from . import views

app_name = 'leads'

urlpatterns = [
    path('', views.leads_list, name='list'),
    path('create/', views.lead_create, name='create'),
    path('update/<int:pk>/', views.lead_update, name='update'),
    path('delete/<int:pk>/', views.lead_delete, name='delete'),
    path('import/', views.import_leads, name='import'),
    path('export/', views.export_leads, name='export'),
]
