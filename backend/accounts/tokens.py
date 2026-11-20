
import hashlib
import uuid

import jwt
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import RefreshToken, User


class TokenError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code, self.message = code, message


def hash_token(raw):
    return hashlib.sha256(raw.encode()).hexdigest()


def decode_token(token, expected_type):
    try:
        payload = jwt.decode(
            token, settings.JWT_SIGNING_KEY, algorithms=["HS256"],      
            issuer=settings.JWT_ISSUER,
            options={"require": ["exp", "iat", "sub", "jti", "typ"]},
        )
    except jwt.ExpiredSignatureError:
        raise TokenError("token_expired", "Token has expired.")
    except jwt.InvalidTokenError:
        raise TokenError("token_invalid", "Token is invalid.")
    if payload["typ"] != expected_type:
        raise TokenError("token_invalid", "Wrong token type.")
    return payload


def _build(user, typ, lifetime, remember=True):
    now = timezone.now()
    claims = {"iss": settings.JWT_ISSUER, "sub": str(user.id), "role": user.role, "typ": typ,
              "rem": remember, "jti": uuid.uuid4().hex, "iat": now, "exp": now + lifetime}
    return jwt.encode(claims, settings.JWT_SIGNING_KEY, algorithm="HS256"), claims["exp"]


def issue_access_token(user):
    return _build(user, "access", settings.JWT_ACCESS_LIFETIME)[0]


def issue_refresh_token(user, user_agent="", ip=None, remember=True):
    life = settings.JWT_REFRESH_LIFETIME if remember else settings.JWT_REFRESH_LIFETIME_SESSION
    raw, exp = _build(user, "refresh", life, remember)
    RefreshToken.objects.create(user_id=user.id, token_hash=hash_token(raw),
                                user_agent=(user_agent or "")[:255], ip_address=ip, expires_at=exp)
    return raw


def issue_token_pair(user, user_agent="", ip=None, remember=True):
    return issue_access_token(user), issue_refresh_token(user, user_agent, ip, remember)


def authenticate_access_token(token):
    user = User.objects.filter(pk=decode_token(token, "access")["sub"]).first()
    
    if user is None or not user.can_sign_in:
        raise TokenError("account_inactive", "Account is not active.")
    return user


def rotate_refresh_token(raw, user_agent="", ip=None):
    """Returns (user, new_access, new_refresh, remember) or raises TokenError."""
    remember = decode_token(raw, "refresh").get("rem", True)
    now, error, result = timezone.now(), None, None

    with transaction.atomic():
        row = (RefreshToken.objects.select_for_update(of=("self",)).select_related("user")
               .filter(token_hash=hash_token(raw)).first())     # row lock: two refreshes can't both win
        if row is None:
            error = TokenError("token_invalid", "Unknown refresh token.")
        elif row.revoked_at is not None:
            if now - row.revoked_at <= settings.JWT_REFRESH_REUSE_GRACE:
                error = TokenError("token_rotated", "Token was just rotated.")      # two tabs racing: benign
            else:
                RefreshToken.objects.filter(user_id=row.user_id, revoked_at__isnull=True).update(revoked_at=now)
                error = TokenError("token_reused", "Reuse detected; all sessions revoked.")
        elif row.expires_at <= now:
            error = TokenError("token_expired", "Refresh token has expired.")
        elif not row.user.can_sign_in:
            error = TokenError("account_inactive", "Account is not active.")
        else:
            row.revoked_at = now
            row.save(update_fields=["revoked_at"])
            result = (row.user, *issue_token_pair(row.user, user_agent, ip, remember), remember)
    if error:               
        raise error
    return result


def revoke_refresh_token(raw):
    RefreshToken.objects.filter(token_hash=hash_token(raw), revoked_at__isnull=True).update(revoked_at=timezone.now())


def revoke_all_for_user(user_id):
    return RefreshToken.objects.filter(user_id=user_id, revoked_at__isnull=True).update(revoked_at=timezone.now())
