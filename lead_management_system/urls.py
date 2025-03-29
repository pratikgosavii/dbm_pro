from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('leads/', include('leads.urls')),
    path('projects/', include('projects.urls')),
    path('employees/', include('employees.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('payments/', include('payments.urls')),
    path('chat/', include('chat.urls')),
    path('', include('dashboard.urls')),  # Redirect root to dashboard
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
