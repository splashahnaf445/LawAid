"""
Account models: User and ClientProfile (LawyerProfile lives in lawyers.models).

Integration note (integration/merge-all): this file combines
  * Ahnaf's Django-managed models (migrations, PermissionsMixin, staff flags) - the runnable base, and
  * Usama's schema-mapped fields (db/schema.sql: users, client_profiles) and the Language choices
    his registration serializer uses.
Table names follow db/schema.sql. Columns that still differ from schema.sql are listed in the
integration PR for Ahnaf and Usama to align.
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
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
    # Usama (SYS-18): values of the schema's language_code enum.
    BN = 'bn', 'Bangla'
    EN = 'en', 'English'


class User(AbstractBaseUser, PermissionsMixin):
    """
    Central User model representing all platform actors.
    Reflects the 'users' table in db/schema.sql.
    SRS: FR-1, FR-4, FR-34.
    """
    id = models.UUIDField(primary_key=True, default=generate_uuid, editable=False)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CLIENT)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    preferred_language = models.CharField(max_length=5, default=Language.BN, choices=Language.choices)
    status = models.CharField(max_length=25, choices=AccountStatus.choices, default=AccountStatus.ACTIVE)
    avatar_url = models.TextField(null=True, blank=True)
    two_factor_enabled = models.BooleanField(default=False)

    email_verified_at = models.DateTimeField(null=True, blank=True)
    phone_verified_at = models.DateTimeField(null=True, blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    suspended_reason = models.TextField(null=True, blank=True)
    suspended_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # soft delete (NFR-8)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'role']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.role}) - {self.email}"

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN or self.is_staff or self.is_superuser

    # Statuses allowed to sign in. Saker's login (SYS-19) allowed only 'active'; registration
    # (Usama, SYS-18) creates lawyers as 'pending_verification', and they must be able to log in
    # to see their verification status, so that status is allowed too.
    SIGN_IN_STATUSES = (AccountStatus.ACTIVE, AccountStatus.PENDING_VERIFICATION)

    @property
    def can_sign_in(self):
        """Saker (SYS-19): used by the cookie-based login / refresh / access-token checks."""
        return self.status in self.SIGN_IN_STATUSES and self.deleted_at is None and self.is_active


class ClientProfile(models.Model):
    """
    Client profile reflecting the 'client_profiles' table in db/schema.sql.
    Fields from both branches are kept: Usama's schema columns (gender ... address) and
    Ahnaf's nid_number / emergency_contact / timestamps.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='client_profile'
    )
    # Usama (SYS-18) - columns from db/schema.sql
    gender = models.CharField(max_length=12, default='undisclosed')
    date_of_birth = models.DateField(null=True, blank=True)
    organization_name = models.TextField(null=True, blank=True)
    division = models.TextField(null=True, blank=True)
    district = models.TextField(null=True, blank=True)
    # Shared by both branches
    address = models.TextField(blank=True, default='')
    # Ahnaf (SYS-21) - not in db/schema.sql yet
    nid_number = models.CharField(max_length=30, blank=True, null=True)
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'client_profiles'
        verbose_name = 'Client Profile'
        verbose_name_plural = 'Client Profiles'

    def __str__(self):
        return f"Client: {self.user.full_name}"


class RefreshToken(models.Model):
    """
    Saker (SYS-19): refresh tokens issued by the cookie-based login (db/schema.sql: refresh_tokens).
    Only a SHA-256 hash of each token is stored; rotation revokes the old row.

    Integration note: on Saker's branch this was an unmanaged model pointing at his own
    unmanaged User. It now references the shared User model and is created by migration
    accounts.0004 like the other tables.
    """
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
