from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from .tokens import TokenError, authenticate_access_token


class JWTAuthentication(BaseAuthentication):
    

    def authenticate(self, request):
        parts = get_authorization_header(request).split()
        if not parts or parts[0].lower() != b"bearer":
            return None
        if len(parts) != 2:
            raise AuthenticationFailed({"detail": "Malformed header.", "code": "token_invalid"})
        try:
            return authenticate_access_token(parts[1].decode()), None
        except TokenError as e:
            # Integration: a token this class cannot decode may be a SimpleJWT token from
            # /api/auth/token/ (kept for the API contract). Return None so the next class in
            # DEFAULT_AUTHENTICATION_CLASSES can try it; if nothing accepts it the request still gets 401.
            if e.code == "token_invalid":
                return None
            raise AuthenticationFailed({"detail": e.message, "code": e.code})

    def authenticate_header(self, request):
        return "Bearer"


class NoAuth(BaseAuthentication):
    """
    For public auth endpoints (login / refresh / logout).

    With `authentication_classes = []` DRF has no WWW-Authenticate header to send, so it
    silently turns every AuthenticationFailed (401) into a 403. This class never
    authenticates anyone but gives DRF the header, so failures stay 401.
    """

    def authenticate(self, request):
        return None

    def authenticate_header(self, request):
        return "Bearer"
