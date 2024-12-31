from django.contrib.auth.views import LoginView
from django.views.generic import View
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages




class CustomLoginView(LoginView):
    template_name = 'authentication/login.html'

    def form_valid(self, form):
        messages.success(self.request, 'Você foi autenticado com sucesso!')
        return super().form_valid(form)

class LogoutRedirectView(View):
    """Handles logout via GET and redirects to the login page."""
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse('auth:login'))