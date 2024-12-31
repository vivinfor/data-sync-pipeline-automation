from datetime import datetime
import logging
import requests

class LoginAuditMiddleware:
    """Middleware para registrar eventos de login e logout."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated and request.path in ["/login/", "/logout/"]:
            logger = logging.getLogger("django")
            action = "LOGIN" if request.path == "/login/" else "LOGOUT"
            logger.info(
                f"{action} - User: {request.user.username}, "
                f"IP: {self.get_client_ip(request)}, "
                f"Browser: {request.META.get('HTTP_USER_AGENT', 'Unknown')}"
            )
        return None

    @staticmethod
    def get_client_ip(request):
        """Obtém o IP do cliente de forma segura."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")

from django.contrib.sessions.models import Session
from django.contrib.auth.models import User

class SingleSessionMiddleware:
    """Middleware para garantir que um usuário tenha apenas uma sessão ativa."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            current_session_key = request.session.session_key
            user_sessions = Session.objects.filter(expire_date__gte=datetime.now())
            for session in user_sessions:
                data = session.get_decoded()
                if data.get('_auth_user_id') == str(request.user.id) and session.session_key != current_session_key:
                    session.delete()
        response = self.get_response(request)
        return response


class GeoIPAuthMiddleware:
    """Middleware para restringir logins com base na localização geográfica."""

    ALLOWED_COUNTRIES = ["BR"]  # Permitir apenas logins do Brasil
    GEOIP_SERVICE_URL = "http://ip-api.com/json/{}"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/login/" and request.method == "POST":
            client_ip = self.get_client_ip(request)
            location_data = self.get_location(client_ip)
            if location_data and location_data.get("countryCode") not in self.ALLOWED_COUNTRIES:
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden("Login from your location is not allowed.")
        response = self.get_response(request)
        return response

    @staticmethod
    def get_client_ip(request):
        """Obtém o IP do cliente."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")

    def get_location(self, ip):
        """Obtém informações de localização com base no IP."""
        try:
            response = requests.get(self.GEOIP_SERVICE_URL.format(ip))
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return None
