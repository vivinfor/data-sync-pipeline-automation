from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib import messages

class CustomLoginView(LoginView):
    template_name = 'authentication/login.html'

    def form_valid(self, form):
        messages.success(self.request, 'Você foi autenticado com sucesso!')
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('auth:login')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'Você foi desconectado com sucesso!')
        return super().dispatch(request, *args, **kwargs)

