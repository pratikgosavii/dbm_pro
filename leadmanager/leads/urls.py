from django.urls import path
from . import views

app_name = 'leads'

urlpatterns = [
    path('', views.lead_list, name='lead_list'),
    path('<int:pk>/', views.lead_detail, name='lead_detail'),
    path('create/', views.lead_create, name='lead_create'),
    path('<int:pk>/update/', views.lead_update, name='lead_update'),
    path('import/', views.lead_import, name='lead_import'),
    path('export/', views.lead_export, name='lead_export'),
    path('assign/', views.lead_assign, name='lead_assign'),
    path('facebook/', views.facebook_leads, name='facebook_leads'),
]
