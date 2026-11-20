"""
Registration serializers for the two roles (FR-1).

* The role is fixed by the endpoint - it is never read from the request body, so a
  client cannot register themselves as an admin/lawyer by adding "role" to the JSON.
* Duplicate email / phone / Bar Council no. are rejected up front with a field error,
  and again at INSERT time (unique constraints) to close the check-then-insert race.
* The user row and its profile are written in one transaction: no half-created accounts.
"""
from contextlib import contextmanager

from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, connection, transaction
from rest_framework import serializers

from lawyers.models import Court, PracticeArea

from . import validators as rules
from .models import AccountStatus, ClientProfile, Language, LawyerProfile, User, UserRole

EMAIL_TAKEN = "An account with this email already exists. Try logging in instead."
PHONE_TAKEN = "This mobile number is already registered."
BAR_NO_TAKEN = "This Bar Council number is already registered."


def _classify_integrity_error(exc):
    """Map a unique-constraint violation to (field, message), or (None, None) if unknown."""
    diag = getattr(exc.__cause__, "diag", None)
    name = (getattr(diag, "constraint_name", None) or str(exc)).lower()
    if "bar_council" in name:
        return "bar_council_no", BAR_NO_TAKEN
    if "email" in name:
        return "email", EMAIL_TAKEN
    if "phone" in name:
        return "phone", PHONE_TAKEN
    return None, None


@contextmanager
def translate_integrity_errors():
    """Turn a lost uniqueness race into the same field error the up-front check gives."""
    try:
        yield
    except IntegrityError as exc:
        field, message = _classify_integrity_error(exc)
        if field is None:
            raise
        raise serializers.ValidationError({field: [message]}) from exc


class BaseRegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(write_only=True, trim_whitespace=False, max_length=128)
    password_confirm = serializers.CharField(write_only=True, trim_whitespace=False, max_length=128)
    preferred_language = serializers.ChoiceField(choices=Language.choices, default=Language.BN)
    accept_terms = serializers.BooleanField()

    # ---- field level -------------------------------------------------------
    def validate_full_name(self, value):
        try:
            return rules.clean_full_name(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc))

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():  # includes soft-deleted accounts
            raise serializers.ValidationError(EMAIL_TAKEN, code="duplicate_email")
        return value

    def validate_password(self, value):
        try:
            password_validation.validate_password(value)  # length, common-password, complexity
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

    def validate_accept_terms(self, value):
        if value is not True:
            raise serializers.ValidationError("You must accept the terms to create an account.")
        return value

    def _clean_phone(self, value):
        if not value:
            return None
        try:
            phone = rules.normalize_bd_phone(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc))
        if User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError(PHONE_TAKEN, code="duplicate_phone")
        return phone

    # ---- object level ------------------------------------------------------
    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": ["Passwords do not match."]})
        attrs.pop("password_confirm")
        # Second pass with a user object so the "too similar to your email/name" rule can run.
        probe = User(email=attrs["email"], full_name=attrs["full_name"])
        try:
            password_validation.validate_password(attrs["password"], user=probe)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)})
        return attrs

    # ---- output (never echo the password) ---------------------------------
    def to_representation(self, user):
        return {
            "id": str(user.pk),
            "role": user.role,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "status": user.status,
        }


class ClientRegisterSerializer(BaseRegisterSerializer):
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True, allow_null=True)

    def validate_phone(self, value):
        return self._clean_phone(value)

    def create(self, validated_data):
        with translate_integrity_errors(), transaction.atomic():
            user = User.objects.create_user(
                email=validated_data["email"],
                password=validated_data["password"],
                role=UserRole.CLIENT,
                full_name=validated_data["full_name"],
                phone=validated_data.get("phone"),
                preferred_language=validated_data["preferred_language"],
                status=AccountStatus.ACTIVE,
            )
            ClientProfile.objects.create(user=user)
        return user


class LawyerRegisterSerializer(BaseRegisterSerializer):
    phone = serializers.CharField(max_length=32)
    primary_court = serializers.PrimaryKeyRelatedField(
        queryset=Court.objects.all(),
        error_messages={
            "required": "Select your primary court.",
            "does_not_exist": "Select a valid court.",
            "incorrect_type": "Select a valid court.",
        },
    )
    bar_council_no = serializers.CharField(max_length=40)
    bar_association = serializers.CharField(max_length=120)
    practice_areas = serializers.PrimaryKeyRelatedField(
        many=True,
        allow_empty=False,
        queryset=PracticeArea.objects.all(),
        error_messages={
            "empty": "Select at least one practice area.",
            "required": "Select at least one practice area.",
            "does_not_exist": "Select valid practice areas.",
            "incorrect_type": "Select valid practice areas.",
        },
    )
    chamber_address = serializers.CharField(max_length=300)
    consultation_fee = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=0, required=False, default=0
    )
    two_factor_enabled = serializers.BooleanField(required=False, default=False)

    def validate_phone(self, value):
        return self._clean_phone(value)

    def validate_bar_council_no(self, value):
        try:
            value = rules.normalize_bar_council_no(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc))
        if LawyerProfile.objects.filter(bar_council_no__iexact=value).exists():
            raise serializers.ValidationError(BAR_NO_TAKEN, code="duplicate_bar_council_no")
        return value

    def validate_practice_areas(self, value):
        unique = list({area.pk: area for area in value}.values())
        if len(unique) > 12:
            raise serializers.ValidationError("Select at most 12 practice areas.")
        return unique

    def validate(self, attrs):
        attrs = super().validate(attrs)
        # "Adv. Tanvir Ahmed" -> honorific "Adv." + full_name "Tanvir Ahmed" (as in seed.sql)
        honorific, name = rules.split_honorific(attrs["full_name"])
        if len(name) < 2:
            raise serializers.ValidationError({"full_name": ["Enter your full name after the honorific."]})
        attrs["honorific"], attrs["full_name"] = honorific, name
        return attrs

    def create(self, validated_data):
        court = validated_data["primary_court"]
        with translate_integrity_errors(), transaction.atomic():
            user = User.objects.create_user(
                email=validated_data["email"],
                password=validated_data["password"],
                role=UserRole.LAWYER,
                full_name=validated_data["full_name"],
                phone=validated_data["phone"],
                preferred_language=validated_data["preferred_language"],
                two_factor_enabled=validated_data["two_factor_enabled"],
                # Lawyers cannot be booked until an admin approves them (FR-3).
                status=AccountStatus.PENDING_VERIFICATION,
            )
            LawyerProfile.objects.create(
                user=user,
                honorific=validated_data["honorific"],
                bar_council_no=validated_data["bar_council_no"],
                bar_association=validated_data["bar_association"],
                primary_court=court,
                chamber_address=validated_data["chamber_address"],
                district=court.district,
                consultation_fee=validated_data["consultation_fee"],
            )
            # lawyer_practice_areas has a composite PK (lawyer_id, practice_area_id), which Django
            # models can't express before 5.2's CompositePrimaryKey - a plain INSERT is simplest.
            with connection.cursor() as cursor:
                cursor.executemany(
                    "INSERT INTO lawyer_practice_areas (lawyer_id, practice_area_id) VALUES (%s, %s)",
                    [(user.pk, area.pk) for area in validated_data["practice_areas"]],
                )
        return user

    def to_representation(self, user):
        data = super().to_representation(user)
        profile = user.lawyer_profile
        data.update(
            honorific=profile.honorific,
            bar_council_no=profile.bar_council_no,
            verification_status=profile.verification_status,
        )
        return data
