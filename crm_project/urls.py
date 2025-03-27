from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('leads/', include('leads.urls')),
    path('projects/', include('projects.urls')),
    path('employees/', include('employees.urls')),
    path('payments/', include('payments.urls')),
    path('reports/', include('reports.urls')),
    path('chat/', include('chat.urls')),
]

# Add static and media URLs in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
