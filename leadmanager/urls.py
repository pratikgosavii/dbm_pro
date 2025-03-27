"""
URL configuration for leadmanager project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/'), name='home'),
    path('accounts/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('leads/', include('apps.leads.urls')),
    path('projects/', include('apps.projects.urls')),
    path('payments/', include('apps.payments.urls')),
    path('employees/', include('apps.employees.urls')),
]
