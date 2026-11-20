"""
/api/auth/ routes.

Integration note: Saker's cookie-based login (SYS-19) is the main login flow used by the
frontend: login/ refresh/ logout/ logout-all/ me/. Ahnaf's SimpleJWT endpoints stay at
/api/auth/token/ and /api/auth/token/refresh/ (config/urls.py) for the API contract.
Ahnaf's earlier login/ and me/ routes were replaced by Saker's views; the URL names
'auth-login' and 'current-user' are kept.
"""
from django.urls import path

from .password_reset_views import ForgotPasswordView, ResetPasswordView
from .views import (
    LoginView,
    LogoutAllView,
    LogoutView,
    MeView,
    RefreshView,
    RegisterClientView,
    RegisterLawyerView,
)

urlpatterns = [
    # Saker (SYS-19)
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("logout-all/", LogoutAllView.as_view(), name="auth-logout-all"),
    path("me/", MeView.as_view(), name="current-user"),
    # Usama (SYS-18) - same paths and names in both branches
    path("register/client/", RegisterClientView.as_view(), name="register-client"),
    path("register/lawyer/", RegisterLawyerView.as_view(), name="register-lawyer"),
    # Password Recovery (SYS-20 / SRS FR-5 – Mashruba Aktar)
    path('password/forgot/', ForgotPasswordView.as_view(), name='password-forgot'),
    path('password/reset/', ResetPasswordView.as_view(), name='password-reset'),
]
