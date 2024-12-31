from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.urls import path, include
from django.views.generic import RedirectView


def health_check(request):
    return HttpResponse("OK")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls', namespace='auth')), 
    path('health/', health_check, name='health'),
    path('', RedirectView.as_view(pattern_name='dashboard:deliveries_dashboard', permanent=False), name='home'),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)