
"""
Django settings for virtual_fashion_store project.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================================
# ENVIRONMENT-AWARE SETTINGS
# ==========================================

# In production, set these environment variables on your host:
#   SECRET_KEY  — a long random string
#   DEBUG       — set to "False" in production
#   ALLOWED_HOSTS — comma-separated list of your domain(s)
#   DATABASE_URL — full postgres connection string (auto-used by Railway/Render)

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-CHANGE-THIS-BEFORE-DEPLOYMENT')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

_ALLOWED = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost')
ALLOWED_HOSTS = [h.strip() for h in _ALLOWED.split(',') if h.strip()]

# Render automatically sets RENDER_EXTERNAL_HOSTNAME (e.g. your-app.onrender.com)
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Trust proxy headers for CSRF & HTTPS
CSRF_TRUSTED_ORIGINS = [
    f"https://{h.lstrip('.')}" for h in ALLOWED_HOSTS if not h.startswith(('127.', 'localhost'))
]
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")


# ==========================================
# INSTALLED APPLICATIONS
# ==========================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'fashion',
]


# ==========================================
# MIDDLEWARE
# ==========================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # ← serves static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# URL configuration
ROOT_URLCONF = 'virtual_fashion_store.urls'


# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# WSGI
WSGI_APPLICATION = 'virtual_fashion_store.wsgi.application'


# ==========================================
# DATABASE
# ==========================================

# Supports DATABASE_URL env var (Railway/Render set this automatically)
_db_url = os.environ.get('DATABASE_URL', '')

if _db_url:
    from urllib.parse import urlparse, unquote
    _url = urlparse(_db_url)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': _url.path.lstrip('/'),
            'USER': unquote(_url.username or ''),
            'PASSWORD': unquote(_url.password or ''),
            'HOST': _url.hostname or 'localhost',
            'PORT': str(_url.port or 5432),
        }
    }
else:
    # Local development — use local PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'virtual_fashion_db'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', '2003'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }


# ==========================================
# PASSWORD VALIDATION
# ==========================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ==========================================
# INTERNATIONALIZATION
# ==========================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True


# ==========================================
# STATIC FILES  (WhiteNoise serves in prod)
# ==========================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Note: Don't add STATICFILES_DIRS when APP_DIRS=True handles fashion/static automatically

# WhiteNoise: gzip + long-term caching in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ==========================================
# DEFAULT PRIMARY KEY
# ==========================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==========================================
# TREAD ADMIN PANEL AUTHENTICATION SETTINGS
# ==========================================

LOGIN_URL = '/admin-login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/admin-login/'


# ==========================================
# PRODUCTION SECURITY (auto-enabled when DEBUG=False)
# ==========================================

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000       # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')