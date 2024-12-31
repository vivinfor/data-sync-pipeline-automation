import os
from pathlib import Path
import logging
from dotenv import load_dotenv

# ========== Configurações Básicas ==========
logger = logging.getLogger(__name__)

# Diretório Base
BASE_DIR = Path(__file__).resolve().parent.parent
logger.info(f"Base Directory: {BASE_DIR}")

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key')


# Configuração de DEBUG
DEBUG = os.getenv('DEBUG')

# Configuração principal
ALLOWED_HOSTS = ['*']
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/auth/login/'

# ========== Configurações de Aplicativos ==========
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'app', 
    'dashboard', 
    'authentication',  

    'tailwind',
    'theme',
]

# ========== Configurações de Middleware ==========
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# Configuração de URL
ROOT_URLCONF = 'app.urls'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========== Configurações de Templates ==========
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app.context_processors.sidebar_context',
            ],
        },
    },
]


# ========== Configurações Estáticas ==========
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Diretório de arquivos estáticos
]
TAILWIND_APP_NAME = 'theme'


# ========== Configurações de Banco de Dados ==========
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('CONTAINER_NAME', 'azure_devops_db'),
        'USER': os.getenv('DB_USER', 'myuser'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'mypassword'),
        'HOST': os.getenv('DB_HOST', 'db'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}


# ========== Configurações de Segurança ==========
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False') == 'True'
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'False') == 'True'
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'

# ========== Configurações de Internacionalização ==========
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True
USE_TZ = True

# ========== Configurações de Arquivos e Mídia ==========
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

