"""
Django mappings onto the tables defined in db/schema.sql.

All models are `managed = False`: the SQL file owns the DDL (enums, citext, composite
role-pinning FKs, triggers). Only the columns the app reads/writes are mapped; every
other column keeps its database default (created_at, avg_rating, session_minutes ...).
Extend a model when a later ticket needs another column.
"""
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

from core.ids import uuid7

from .managers import UserManager


class UserRole(models.TextChoices):
    CLIENT = "client"
    LAWYER = "lawyer"
    ADMIN = "admin"


class AccountStatus(models.TextChoices):
    INVITED = "invited"
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class Language(models.TextChoices):
    BN = "bn"
    EN = "en"


class VerificationStatus(models.TextChoices):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    role = models.CharField(max_length=10, choices=UserRole.choices)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254, unique=True)  # citext in the DB -> case-insensitive unique
    phone = models.CharField(max_length=14, unique=True, null=True, blank=True)
    # AbstractBaseUser's `password` / `last_login` map to the schema's column names.
    password = models.CharField(max_length=128, db_column="password_hash")
    last_login = models.DateTimeField(db_column="last_login_at", null=True, blank=True)
    preferred_language = models.CharField(max_length=2, choices=Language.choices, default=Language.BN)
    status = models.CharField(max_length=24, choices=AccountStatus.choices, default=AccountStatus.ACTIVE)
    two_factor_enabled = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    phone_verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # soft delete (NFR-8)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        db_table = "users"
        managed = False

    def __str__(self):
        return f"{self.email} ({self.role})"


class ClientProfile(models.Model):
    # `role` is intentionally not mapped: the column defaults to 'client' and a CHECK +
    # composite FK (user_id, role) -> users(id, role) guarantee it matches users.role.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE, related_name="client_profile"
    )
    gender = models.CharField(max_length=12, default="undisclosed")
    date_of_birth = models.DateField(null=True, blank=True)
    organization_name = models.TextField(null=True, blank=True)
    division = models.TextField(null=True, blank=True)
    district = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "client_profiles"
        managed = False


class LawyerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE, related_name="lawyer_profile"
    )
    honorific = models.TextField(null=True, blank=True)
    bar_council_no = models.TextField(unique=True)
    bar_association = models.TextField(null=True, blank=True)
    primary_court = models.ForeignKey("lawyers.Court", null=True, on_delete=models.SET_NULL, db_column="primary_court_id")
    chamber_address = models.TextField(null=True, blank=True)
    district = models.TextField(null=True, blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    verification_status = models.CharField(
        max_length=10, choices=VerificationStatus.choices, default=VerificationStatus.PENDING
    )

    class Meta:
        db_table = "lawyer_profiles"
        managed = False
