from django.urls import path
from .views import (
    CustomLoginView,
    LogoutRedirectView,

)

app_name = 'auth'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutRedirectView.as_view(), name='logout'),
    
]