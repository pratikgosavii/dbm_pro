"""
URL Configuration for the Lead Management System
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/')),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('leads/', include('leads.urls')),
    path('projects/', include('projects.urls')),
    path('accounting/', include('accounting.urls')),
    path('employees/', include('employees.urls')),
]

# Customize admin site
admin.site.site_header = 'Lead Management System Administration'
admin.site.site_title = 'Lead Management Admin'
admin.site.index_title = 'Welcome to Lead Management System'
