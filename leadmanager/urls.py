"""
URL configuration for leadmanager project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('leads/', include('leads.urls')),
    path('projects/', include('projects.urls')),
    path('employees/', include('employees.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('', include('dashboard.urls')),  # Make dashboard the default landing page
]
