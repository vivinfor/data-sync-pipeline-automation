# dashboard/urls.py

from django.urls import path
from .views import (
    DeliveriesView,
    PerformanceView,
    
)

app_name = 'dashboard'

urlpatterns = [
    path('performance/', PerformanceView.as_view(), name='performance_dashboard'),
    path('deliveries/', DeliveriesView.as_view(), name='deliveries_dashboard'),

]
