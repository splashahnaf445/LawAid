from functools import lru_cache

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from rest_framework import generics
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .authentication import NoAuth
from .models import User
from .serializers import (
    ClientRegisterSerializer,
    CustomTokenObtainPairSerializer,
    LawyerRegisterSerializer,
    LoginSerializer,
    UserSerializer,
)
from .tokens import TokenError, issue_token_pair, revoke_all_for_user, revoke_refresh_token, rotate_refresh_token


# ---------------------------------------------------------------------------
# Registration - Usama (SYS-18) + Ahnaf's document upload (SYS-21)
# ---------------------------------------------------------------------------
class _RegisterView(generics.CreateAPIView):
    """
    Usama (SYS-18): public, throttled (settings: DEFAULT_THROTTLE_RATES['register']).
    Returns 201 + the new account.
    """

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "register"


class RegisterClientView(_RegisterView):
    """Client registration endpoint (FR-1)."""
    serializer_class = ClientRegisterSerializer


class RegisterLawyerView(_RegisterView):
    """
    Lawyer registration (FR-1) with mandatory NID and Bar Council certificate upload (FR-2).
    Uploaded documents are encrypted at rest (NFR-1, NFR-4). Multipart is required for the files.
    """
    serializer_class = LawyerRegisterSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


# ---------------------------------------------------------------------------
# Ahnaf (SYS-21/22): SimpleJWT token endpoint, kept at /api/auth/token/ for the API contract.
# The frontend uses Saker's cookie-based login below (see docs/api/README.md).
# ---------------------------------------------------------------------------
class CustomTokenObtainPairView(TokenObtainPairView):
    """JWT token endpoint returning tokens and user verification payload."""
    serializer_class = CustomTokenObtainPairSerializer


# ---------------------------------------------------------------------------
# Saker (SYS-19): login / refresh (httpOnly cookie) / logout / me - the main login flow
# ---------------------------------------------------------------------------
INVALID = {"detail": "Invalid email or password.", "code": "invalid_credentials"}


@lru_cache(maxsize=1)
def _dummy_hash():
    return make_password("not-a-real-password")


def _meta(request):
    return request.META.get("HTTP_USER_AGENT", ""), request.META.get("REMOTE_ADDR")


def _require_xhr(request):

    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        raise PermissionDenied({"detail": "Missing X-Requested-With header.", "code": "csrf_check_failed"})


def _set_cookie(resp, token, remember=True):
    resp.set_cookie(settings.JWT_REFRESH_COOKIE, token,
                    max_age=int(settings.JWT_REFRESH_LIFETIME.total_seconds()) if remember else None,
                    httponly=True, secure=settings.JWT_COOKIE_SECURE, samesite=settings.JWT_COOKIE_SAMESITE,
                    path=settings.JWT_REFRESH_COOKIE_PATH)


def _clear_cookie(resp):
    resp.delete_cookie(settings.JWT_REFRESH_COOKIE, path=settings.JWT_REFRESH_COOKIE_PATH,
                       samesite=settings.JWT_COOKIE_SAMESITE)


def _session(user, access, refresh, remember=True):
    resp = Response({"access": access, "user": UserSerializer(user).data,
                     "access_expires_in": int(settings.JWT_ACCESS_LIFETIME.total_seconds())})
    _set_cookie(resp, refresh, remember)
    return resp


class LoginView(APIView):
    authentication_classes, permission_classes = [NoAuth], [AllowAny]
    throttle_classes, throttle_scope = [ScopedRateThrottle], "login"

    def post(self, request):
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        email, password = s.validated_data["email"], s.validated_data["password"]

        # Integration: case-insensitive like the schema's citext email column.
        user = User.objects.filter(email__iexact=email, deleted_at__isnull=True).first()

        if user is None:
            check_password(password, _dummy_hash())
            raise AuthenticationFailed(INVALID)
        # Integration: the shared User model stores the hash in `password` (Django's AbstractBaseUser).
        if not user.check_password(password):
            raise AuthenticationFailed(INVALID)
        # Integration: `can_sign_in` also allows 'pending_verification' (new lawyers).
        if not user.can_sign_in:
            raise PermissionDenied({"detail": f"Account is {user.status.replace('_', ' ')}.",
                                    "code": f"account_{user.status}"})
        portal = s.validated_data.get("portal")
        if portal and user.role != portal:
            raise PermissionDenied({"detail": f"This is a {user.role} account. Please use the {user.role} portal.",
                                    "code": "wrong_portal"})
        remember = s.validated_data["remember"]
        User.objects.filter(pk=user.pk).update(last_login=timezone.now())
        access, refresh = issue_token_pair(user, *_meta(request), remember=remember)
        return _session(user, access, refresh, remember)


class RefreshView(APIView):
    authentication_classes, permission_classes = [NoAuth], [AllowAny]
    throttle_classes, throttle_scope = [ScopedRateThrottle], "refresh"

    def post(self, request):
        _require_xhr(request)
        raw = request.COOKIES.get(settings.JWT_REFRESH_COOKIE)
        if not raw:
            raise AuthenticationFailed({"detail": "No refresh token.", "code": "no_refresh_token"})
        try:
            user, access, refresh, remember = rotate_refresh_token(raw, *_meta(request))
        except TokenError as e:
            resp = Response({"detail": e.message, "code": e.code}, status=401)
            if e.code != "token_rotated":
                _clear_cookie(resp)
            return resp
        return _session(user, access, refresh, remember)


class LogoutView(APIView):
    authentication_classes, permission_classes = [NoAuth], [AllowAny]

    def post(self, request):
        _require_xhr(request)
        raw = request.COOKIES.get(settings.JWT_REFRESH_COOKIE)
        if raw:
            revoke_refresh_token(raw)
        resp = Response(status=204)
        _clear_cookie(resp)
        return resp


class LogoutAllView(APIView):
    """Sign out of every device (needs a valid access token)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        _require_xhr(request)
        revoke_all_for_user(request.user.id)
        resp = Response(status=204)
        _clear_cookie(resp)
        return resp


class MeView(APIView):
    """
    Current user. Integration note: replaces Ahnaf's CurrentUserView at /api/auth/me/ (same URL
    name 'current-user'); the payload includes his verification fields (see UserSerializer).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
