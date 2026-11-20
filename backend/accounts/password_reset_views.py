"""
Views for password recovery (SYS-20 / SRS FR-5).

POST /api/auth/password/forgot/   – ForgotPasswordView
POST /api/auth/password/reset/    – ResetPasswordView

Author: Mashruba Aktar
Jira:   SYS-20
"""

import logging

from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .password_reset import PasswordResetToken
from .password_reset_serializers import ForgotPasswordSerializer, ResetPasswordSerializer

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SUCCESS_MESSAGE = "If an account matches, a password reset link has been sent."


def _build_reset_link(raw_token: str, request=None) -> str:
    """
    Build the front-end password-reset URL.
    Uses FRONTEND_URL from settings/env; falls back to the API origin in dev.
    """
    base = getattr(settings, "FRONTEND_URL", "")
    if not base and request is not None:
        base = request.build_absolute_uri("/").rstrip("/")
    base = base.rstrip("/")
    return f"{base}/reset-password?token={raw_token}"


def _dispatch_email_reset(user: User, raw_token: str, request=None) -> None:
    """Send the reset link by email (console in dev, SMTP in prod)."""
    link = _build_reset_link(raw_token, request)
    subject = "LawAid – Password Reset Request"
    body = (
        f"Hello {user.full_name},\n\n"
        f"We received a request to reset your LawAid account password.\n\n"
        f"Click the link below to set a new password (valid for 30 minutes):\n\n"
        f"  {link}\n\n"
        f"If you did not request this, you can ignore this email – your password will not change.\n\n"
        f"— The LawAid Team"
    )
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@lawaid.local")
    send_mail(subject, body, from_email, [user.email], fail_silently=False)


def _dispatch_phone_reset(user: User, raw_token: str, request=None) -> None:
    """
    Phone-based reset: SMS is out of scope this semester.
    Log the link to the console so developers can test the full flow.
    """
    link = _build_reset_link(raw_token, request)
    logger.warning(
        "[LawAid DEV] Phone password reset for %s (%s): %s",
        user.full_name,
        user.phone,
        link,
    )
    # In production this would send an SMS via an approved gateway.


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------


class ForgotPasswordView(APIView):
    """
    POST /api/auth/password/forgot/

    Request body (exactly one of):
        { "email": "user@example.com" }
        { "phone": "+8801713000022" }

    Always returns 200 with the same message regardless of whether a user
    exists, to prevent user-enumeration attacks (SRS FR-5).
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        email = data.get("email")
        phone = data.get("phone")

        # Look up user silently – do NOT reveal existence in the response.
        user = None
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                pass
        elif phone:
            try:
                user = User.objects.get(phone=phone)
            except User.DoesNotExist:
                pass

        if user is not None:
            try:
                _, raw_token = PasswordResetToken.create_for_user(user)
                if email:
                    _dispatch_email_reset(user, raw_token, request)
                else:
                    _dispatch_phone_reset(user, raw_token, request)
            except Exception:
                # Never surface internal errors to the client for this endpoint.
                logger.exception(
                    "Failed to create/send password reset token for user %s", user.id
                )

        return Response(
            {"status": "success", "message": _SUCCESS_MESSAGE},
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(APIView):
    """
    POST /api/auth/password/reset/

    Request body:
        { "token": "<raw_token>", "new_password": "<new_password>" }

    On success:
        200 { "status": "success", "message": "Your password has been reset…" }
    On failure:
        400 { "token": ["This reset link is invalid or has expired."] }
        400 { "new_password": ["<validator message>", …] }
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token_obj: PasswordResetToken = serializer.validated_data["_token_obj"]
        new_password: str = serializer.validated_data["new_password"]
        user: User = token_obj.user

        # Set the new password and persist.
        user.set_password(new_password)
        user.save(update_fields=["password"])

        # Mark token used and invalidate all other unused tokens for this user.
        token_obj.consume()

        # NOTE: SimpleJWT's token_blacklist app is NOT installed in this project
        # (it is not listed in INSTALLED_APPS and not in requirements.txt).
        # Therefore existing refresh tokens for this user are NOT invalidated here.
        # To enable this in future, add 'rest_framework_simplejwt.token_blacklist'
        # to INSTALLED_APPS and use OutstandingToken / BlacklistedToken.

        logger.info("Password reset successfully for user %s", user.id)

        return Response(
            {
                "status": "success",
                "message": "Your password has been reset. Please log in with the new password.",
            },
            status=status.HTTP_200_OK,
        )
