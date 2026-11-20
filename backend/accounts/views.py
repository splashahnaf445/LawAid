from functools import lru_cache

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import User
from .serializers import LoginSerializer, UserSerializer
from .tokens import TokenError, issue_token_pair, revoke_all_for_user, revoke_refresh_token, rotate_refresh_token

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
    authentication_classes, permission_classes = [], [AllowAny]
    throttle_classes, throttle_scope = [ScopedRateThrottle], "login"

    def post(self, request):
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        email, password = s.validated_data["email"], s.validated_data["password"]

        user = User.objects.filter(email=email, deleted_at__isnull=True).first()
        
        if user is None:
            check_password(password, _dummy_hash())
            raise AuthenticationFailed(INVALID)
        if not check_password(password, user.password_hash):
            raise AuthenticationFailed(INVALID)
        if user.status != "active":
            raise PermissionDenied({"detail": f"Account is {user.status.replace('_', ' ')}.",
                                    "code": f"account_{user.status}"})
        portal = s.validated_data.get("portal")
        if portal and user.role != portal:      
            raise PermissionDenied({"detail": f"This is a {user.role} account. Please use the {user.role} portal.",
                                    "code": "wrong_portal"})
        remember = s.validated_data["remember"]
        User.objects.filter(pk=user.pk).update(last_login_at=timezone.now())
        access, refresh = issue_token_pair(user, *_meta(request), remember=remember)
        return _session(user, access, refresh, remember)


class RefreshView(APIView):
    authentication_classes, permission_classes = [], [AllowAny]
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
    authentication_classes, permission_classes = [], [AllowAny]

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

    def post(self, request):
        _require_xhr(request)
        revoke_all_for_user(request.user.id)
        resp = Response(status=204)
        _clear_cookie(resp)
        return resp


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)
