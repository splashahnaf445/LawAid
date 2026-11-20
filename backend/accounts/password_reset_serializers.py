"""
Serializers for password recovery endpoints (SYS-20 / SRS FR-5).

ForgotPasswordSerializer  – validates the request body for POST /api/auth/password/forgot/
ResetPasswordSerializer   – validates the request body for POST /api/auth/password/reset/
"""

from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .password_reset import PasswordResetToken
from .validators import validate_bd_phone, normalize_bd_phone


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Accept EITHER email OR phone – never both, never neither.
    API contract: returns 400 with non_field_errors if the rule is broken.
    """

    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        email = attrs.get("email", "").strip()
        phone = attrs.get("phone", "").strip()

        has_email = bool(email)
        has_phone = bool(phone)

        if has_email and has_phone:
            raise serializers.ValidationError(
                {"non_field_errors": ["Provide either email or phone."]}
            )
        if not has_email and not has_phone:
            raise serializers.ValidationError(
                {"non_field_errors": ["Provide either email or phone."]}
            )

        if has_email:
            # Basic format sanity (EmailField already validates, but be explicit)
            attrs["email"] = email.lower()
            attrs["phone"] = None
        else:
            # Normalize BD phone and validate format
            try:
                normalized = normalize_bd_phone(phone)
                validate_bd_phone(normalized)
            except (DjangoValidationError, Exception) as exc:
                raise serializers.ValidationError({"phone": [str(exc)]})
            attrs["phone"] = normalized
            attrs["email"] = None

        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    """
    Accept token + new_password.
    Validates the token exists and is still valid.
    Validates the new password with Django's AUTH_PASSWORD_VALIDATORS.
    """

    token = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        raw_token = attrs.get("token", "")
        new_password = attrs.get("new_password", "")

        # --- Token check ---
        token_obj = PasswordResetToken.get_valid_by_raw(raw_token)
        if token_obj is None:
            raise serializers.ValidationError(
                {"token": ["This reset link is invalid or has expired."]}
            )

        # --- Password strength check ---
        # validate_password raises DjangoValidationError with a list of messages
        try:
            validate_password(new_password, user=token_obj.user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"new_password": list(exc.messages)})

        attrs["_token_obj"] = token_obj
        return attrs
