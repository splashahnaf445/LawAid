"""
Registration serializers for the two roles (FR-1), verification document upload (FR-2)
and the JWT login payload.

* The role is fixed by the endpoint - it is never read from the request body, so a
  client cannot register themselves as an admin/lawyer by adding "role" to the JSON.
* Duplicate email / phone / Bar Council no. are rejected up front with a field error,
  and again at INSERT time (unique constraints) to close the check-then-insert race.
* The user row and its profile are written in one transaction: no half-created accounts.

Integration note (integration/merge-all):
  * Registration rules are Usama's (SYS-18 owner): password confirmation + complexity,
    accept_terms, honorific split, primary court, practice areas, pending_verification.
  * Ahnaf's SYS-21 work is added on top: lawyers must upload the NID and Bar Council
    certificate, which are stored encrypted; his optional profile fields (headline,
    specialization, years_experience, bio, district), the client address field and the
    login serializer are kept.
"""
from contextlib import contextmanager

from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.encryption import DocumentEncryptionService
from lawyers.models import (
    Court,
    LawyerPracticeArea,
    LawyerProfile,
    LawyerVerificationDocument,
    PracticeArea,
    VerificationDocType,
    VerificationStatus,
)

from . import validators as rules
from .models import AccountStatus, ClientProfile, Language, User, UserRole

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


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Ahnaf (SYS-21/22): returns user payload along with JWT tokens.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        user_info = {
            'id': str(user.id),
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'phone': user.phone,
            'status': user.status,
            'is_admin': user.is_admin,
        }
        if hasattr(user, 'lawyer_profile'):
            lp = user.lawyer_profile
            user_info['verification_status'] = lp.verification_status
            user_info['is_verified'] = lp.is_verified
            user_info['bar_council_no'] = lp.bar_council_no
            user_info['badge'] = lp.get_verification_badge()
        data['user'] = user_info
        return data


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
            "user_id": str(user.pk),  # key used by Ahnaf's response format
            "role": user.role,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "status": user.status,
        }


class ClientRegisterSerializer(BaseRegisterSerializer):
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True, allow_null=True)
    # Ahnaf (SYS-21): optional address stored on client_profiles.address
    address = serializers.CharField(required=False, allow_blank=True, default='')

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
            ClientProfile.objects.create(user=user, address=validated_data.get("address", ""))
        return user

    def to_representation(self, user):
        data = super().to_representation(user)
        data["message"] = "Client registered successfully."
        return data


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

    # Ahnaf (SYS-21): optional profile fields
    honorific = serializers.CharField(max_length=20, required=False, allow_blank=True)
    headline = serializers.CharField(max_length=255, required=False, default='Advocate, High Court Division')
    district = serializers.CharField(max_length=100, required=False, allow_blank=True)
    specialization = serializers.CharField(max_length=255, required=False, default='Civil Litigation, Property Law')
    years_experience = serializers.IntegerField(required=False, default=1, min_value=0)
    bio = serializers.CharField(required=False, allow_blank=True, default='')

    # Ahnaf (SYS-21): mandatory verification documents (FR-2), stored encrypted (NFR-4)
    nid_document = serializers.FileField(write_only=True)
    bar_certificate_document = serializers.FileField(write_only=True)

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

    def validate_nid_document(self, value):
        rules.validate_verification_document(value)
        return value

    def validate_bar_certificate_document(self, value):
        rules.validate_verification_document(value)
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        # "Adv. Tanvir Ahmed" -> honorific "Adv." + full_name "Tanvir Ahmed" (as in seed.sql)
        honorific, name = rules.split_honorific(attrs["full_name"])
        if len(name) < 2:
            raise serializers.ValidationError({"full_name": ["Enter your full name after the honorific."]})
        attrs["honorific"] = honorific or (attrs.get("honorific") or None)
        attrs["full_name"] = name
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
            profile = LawyerProfile.objects.create(
                user=user,
                honorific=validated_data["honorific"],
                bar_council_no=validated_data["bar_council_no"],
                bar_association=validated_data["bar_association"],
                primary_court=court,
                chamber_address=validated_data["chamber_address"],
                district=validated_data.get("district") or court.district or "",
                consultation_fee=validated_data["consultation_fee"],
                headline=validated_data.get("headline", "Advocate, High Court Division"),
                specialization=validated_data.get("specialization", "Civil Litigation, Property Law"),
                years_experience=validated_data.get("years_experience", 1),
                bio=validated_data.get("bio", ""),
                verification_status=VerificationStatus.PENDING,
            )
            # lawyer_practice_areas (composite key in schema.sql) is now a Django model, so the
            # ORM is used instead of a raw INSERT (raw UUID parameters do not bind on SQLite).
            LawyerPracticeArea.objects.bulk_create(
                [LawyerPracticeArea(lawyer=profile, practice_area=area)
                 for area in validated_data["practice_areas"]]
            )
            self._store_documents(profile, validated_data)
        return user

    @staticmethod
    def _store_documents(profile, validated_data):
        """Ahnaf (SYS-21): encrypt and record the NID and Bar Council certificate."""
        for field, doc_type in (
            ("nid_document", VerificationDocType.NID),
            ("bar_certificate_document", VerificationDocType.BAR_CERTIFICATE),
        ):
            uploaded = validated_data.get(field)
            if uploaded is None:
                continue
            saved = DocumentEncryptionService.save_encrypted_file(
                uploaded_file=uploaded,
                lawyer_id=str(profile.user_id),
                doc_type=doc_type,
            )
            LawyerVerificationDocument.objects.create(
                lawyer=profile,
                doc_type=doc_type,
                file_url=saved['file_url'],
                original_filename=saved['original_filename'],
                mime_type=saved['mime_type'],
                file_size_bytes=saved['file_size_bytes'],
                status=VerificationStatus.PENDING,
            )

    def to_representation(self, user):
        data = super().to_representation(user)
        profile = user.lawyer_profile
        data.update(
            honorific=profile.honorific,
            bar_council_no=profile.bar_council_no,
            verification_status=profile.verification_status,
            # Ahnaf's response keys (SYS-21/22)
            lawyer_id=str(user.pk),
            is_verified=profile.is_verified,
            badge=profile.get_verification_badge(),
            message=(
                "Lawyer registration submitted successfully. Your NID and Bar Council certificate "
                "have been securely encrypted and queued for administrator verification."
            ),
            notice=(
                "Your profile will remain hidden from client search results until verification "
                "is approved by a platform administrator (SRS FR-3)."
            ),
        )
        return data


# ---------------------------------------------------------------------------
# Saker (SYS-19): cookie-based login and the current-user payload
# ---------------------------------------------------------------------------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False, write_only=True)
    remember = serializers.BooleanField(required=False, default=True)
    portal = serializers.ChoiceField(choices=["client", "lawyer", "admin"], required=False)


class UserSerializer(serializers.ModelSerializer):
    """
    Saker's user payload (login / refresh / me).
    Integration note: extended with the fields Ahnaf's /api/auth/me/ view returned (phone, status,
    is_admin and, for lawyers, verification_status / is_verified / bar_council_no / badge), because
    /api/auth/me/ is now Saker's MeView and the frontend shows the verification badge from it.
    """
    is_admin = serializers.BooleanField(read_only=True)
    verification_status = serializers.SerializerMethodField()
    is_verified = serializers.SerializerMethodField()
    bar_council_no = serializers.SerializerMethodField()
    badge = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "full_name", "email", "role", "avatar_url", "preferred_language", "two_factor_enabled",
            "phone", "status", "is_admin",
            "verification_status", "is_verified", "bar_council_no", "badge",
        ]

    @staticmethod
    def _lawyer_profile(user):
        return getattr(user, "lawyer_profile", None) if user.role == UserRole.LAWYER else None

    def get_verification_status(self, user):
        profile = self._lawyer_profile(user)
        return profile.verification_status if profile else None

    def get_is_verified(self, user):
        profile = self._lawyer_profile(user)
        return profile.is_verified if profile else None

    def get_bar_council_no(self, user):
        profile = self._lawyer_profile(user)
        return profile.bar_council_no if profile else None

    def get_badge(self, user):
        profile = self._lawyer_profile(user)
        return profile.get_verification_badge() if profile else None
