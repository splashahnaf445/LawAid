import os
from pathlib import Path
from datetime import timedelta
import dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
dotenv.load_dotenv(os.path.join(BASE_DIR, '.env'))
dotenv.load_dotenv(os.path.join(BASE_DIR.parent, '.env'))

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-lawaid-dev-key-2026')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', '*').split(',') if h.strip()]

# Modular Django apps for LawAid
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party packages
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',

    # Core & modular domain apps
    'core.apps.CoreConfig',
    'accounts.apps.AccountsConfig',
    'lawyers.apps.LawyersConfig',
    'appointments.apps.AppointmentsConfig',
    'cases.apps.CasesConfig',
    'messaging.apps.MessagingConfig',
    'payments.apps.PaymentsConfig',
    'reviews.apps.ReviewsConfig',
    'ai_assistant.apps.AiAssistantConfig',
    'platform.apps.PlatformConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database configuration:
# Uses PostgreSQL with schema 'lawaid' when configured, or SQLite fallback for local test execution
DATABASE_URL = os.getenv('DATABASE_URL', '')
if DATABASE_URL.startswith('postgres://') or DATABASE_URL.startswith('postgresql://'):
    import urllib.parse
    url = urllib.parse.urlparse(DATABASE_URL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': url.path[1:],
            'USER': url.username,
            'PASSWORD': url.password,
            'HOST': url.hostname,
            'PORT': url.port or 5432,
            'OPTIONS': {
                'options': '-c search_path=lawaid,public'
            }
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Custom Test Runner (handles raw SQL schema & unmanaged models)
TEST_RUNNER = 'config.test_runner.LawAidTestRunner'

# Password validation
# Integration: Usama's registration rules (SYS-18) - length 8, not similar to email/name,
# not a common password, not all digits, plus upper/lower/number/special (his validator).
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {'NAME': 'accounts.validators.PasswordComplexityValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Encrypted verification documents storage (NFR-4)
ENCRYPTED_DOCUMENTS_DIR = os.path.join(BASE_DIR, 'storage', 'encrypted_documents')
os.makedirs(ENCRYPTED_DOCUMENTS_DIR, exist_ok=True)

# Master encryption key
DOCUMENT_ENCRYPTION_KEY = os.getenv(
    'DOCUMENT_ENCRYPTION_KEY', 
    'c1nwgexw36iltaDC_aCA64MHK2AkBmvxoJK0YdQ4GZY='
)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# DRF configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    # Usama (SYS-18): registration views use ScopedRateThrottle(scope='register');
    # the rate comes from REGISTER_THROTTLE_RATE in his .env.example.
    'DEFAULT_THROTTLE_RATES': {
        'register': os.getenv('REGISTER_THROTTLE_RATE', '20/hour'),
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# Email (SYS-20 / SRS FR-5 – Password Recovery)
# ---------------------------------------------------------------------------
# In development (DEBUG=True) all emails are printed to the terminal.
# In production, set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# and the SMTP_* variables in your environment / .env file.
EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend',
)
EMAIL_HOST          = os.getenv('SMTP_HOST', 'smtp.gmail.com')
EMAIL_PORT          = int(os.getenv('SMTP_PORT', '587'))
EMAIL_USE_TLS       = os.getenv('SMTP_USE_TLS', 'True').lower() in ('true', '1', 't')
EMAIL_HOST_USER     = os.getenv('SMTP_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('SMTP_PASSWORD', '')
DEFAULT_FROM_EMAIL  = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@lawaid.local')

# Front-end base URL used to build the reset link that is sent to the user.
# Override with the real URL in production: FRONTEND_URL=https://lawaid.com
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

# How long a password-reset token stays valid (minutes).
PASSWORD_RESET_TOKEN_EXPIRY_MINUTES = int(
    os.getenv('PASSWORD_RESET_TOKEN_EXPIRY_MINUTES', '30')
)
