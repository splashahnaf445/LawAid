"""
Account models: User and ClientProfile (LawyerProfile lives in lawyers.models).

All tables are created by db/schema.sql, so every model here is managed = False.
Django never creates or alters these tables.
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from core.ids import generate_uuid
from .managers import UserManager


class UserRole(models.TextChoices):
    CLIENT = 'client', 'Client'
    LAWYER = 'lawyer', 'Lawyer'
    ADMIN = 'admin', 'Admin'


class AccountStatus(models.TextChoices):
    INVITED = 'invited', 'Invited'
    PENDING_VERIFICATION = 'pending_verification', 'Pending Verification'
    ACTIVE = 'active', 'Active'
    SUSPENDED = 'suspended', 'Suspended'
    DEACTIVATED = 'deactivated', 'Deactivated'


class Language(models.TextChoices):
    BN = 'bn', 'Bangla'
    EN = 'en', 'English'


class User(AbstractBaseUser):
    """Maps onto the 'users' table in db/schema.sql (FR-1, FR-4, FR-34)."""
    id = models.UUIDField(primary_key=True, default=generate_uuid, editable=False)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CLIENT)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    # schema column names differ from Django's defaults:
    password = models.CharField(max_length=255, db_column='password_hash')
    last_login = models.DateTimeField(db_column='last_login_at', null=True, blank=True)

    preferred_language = models.CharField(max_length=5, default=Language.BN, choices=Language.choices)
    status = models.CharField(max_length=25, choices=AccountStatus.choices, default=AccountStatus.ACTIVE)
    avatar_url = models.TextField(null=True, blank=True)
    two_factor_enabled = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    phone_verified_at = models.DateTimeField(null=True, blank=True)
    suspended_reason = models.TextField(null=True, blank=True)
    suspended_by = models.ForeignKey('self', null=True, blank=True,
                                     on_delete=models.SET_NULL, db_column='suspended_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # soft delete (NFR-8)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'role']

    SIGN_IN_STATUSES = (AccountStatus.ACTIVE, AccountStatus.PENDING_VERIFICATION)

    class Meta:
        db_table = 'users'
        managed = False
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.role}) - {self.email}"

    # Columns the schema doesn't have are derived from role/status instead.
    @property
    def is_active(self):
        return self.status in self.SIGN_IN_STATUSES and self.deleted_at is None

    @property
    def is_staff(self):
        return self.role == UserRole.ADMIN

    @property
    def is_superuser(self):
        return self.role == UserRole.ADMIN

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @property
    def can_sign_in(self):
        """Saker (SYS-19): used by the cookie-based login / refresh / access-token checks."""
        return self.is_active

    # Compatibility alias so existing code that reads/writes last_login_at keeps working.
    @property
    def last_login_at(self):
        return self.last_login

    @last_login_at.setter
    def last_login_at(self, value):
        self.last_login = value

    def has_perm(self, perm, obj=None):
        return self.is_active and self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_active and self.is_superuser


class ClientProfile(models.Model):
    """Maps onto 'client_profiles'. nid_number, emergency_contact, created_at and
    updated_at come from db/django_compat.sql."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,
                                related_name='client_profile')
    gender = models.CharField(max_length=12, default='undisclosed')
    date_of_birth = models.DateField(null=True, blank=True)
    organization_name = models.TextField(null=True, blank=True)
    division = models.TextField(null=True, blank=True)
    district = models.TextField(null=True, blank=True)
    address = models.TextField(blank=True, default='')
    nid_number = models.CharField(max_length=30, blank=True, null=True)
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'client_profiles'
        managed = False
        verbose_name = 'Client Profile'
        verbose_name_plural = 'Client Profiles'

    def __str__(self):
        return f"Client: {self.user.full_name}"


class RefreshToken(models.Model):
    """Saker (SYS-19): maps onto 'refresh_tokens'. Only a SHA-256 hash is stored."""
    id = models.UUIDField(primary_key=True, default=generate_uuid, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id", related_name="+")
    token_hash = models.TextField(unique=True)
    user_agent = models.TextField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "refresh_tokens"
        managed = False