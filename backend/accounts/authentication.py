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
            raise AuthenticationFailed({"detail": e.message, "code": e.code})

    def authenticate_header(self, request):
        return "Bearer"    
