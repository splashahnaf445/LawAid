
import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv(BASE_DIR / ".env")


INSTALLED_APPS = ["corsheaders", "rest_framework", "accounts"]
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",   
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

DATABASES = {"default": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": os.environ.get("DB_NAME", "lawaid"),
    "USER": os.environ.get("DB_USER", "postgres"),
    "PASSWORD": os.environ.get("DB_PASSWORD", ""),
    "HOST": os.environ.get("DB_HOST", "localhost"),
    "PORT": os.environ.get("DB_PORT", "5432"),
    "OPTIONS": {"options": "-c search_path=lawaid,public"},   
}}


JWT_SIGNING_KEY = os.environ.get("JWT_SIGNING_KEY", SECRET_KEY)
JWT_ISSUER = "lawaid"
JWT_ACCESS_LIFETIME = timedelta(minutes=15)
JWT_REFRESH_LIFETIME = timedelta(days=7)            
JWT_REFRESH_LIFETIME_SESSION = timedelta(days=1)    
JWT_REFRESH_REUSE_GRACE = timedelta(seconds=10)
JWT_REFRESH_COOKIE = "lawaid_refresh"
JWT_REFRESH_COOKIE_PATH = "/api/auth/"
JWT_COOKIE_SECURE = not DEBUG
JWT_COOKIE_SAMESITE = "Strict"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["accounts.authentication.JWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_THROTTLE_RATES": {"login": "10/min", "refresh": "60/min"},
    "UNAUTHENTICATED_USER": None,    
}

CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = ["Retry-After"]               

TEST_RUNNER = "accounts.tests.runner.LawAidRunner"
