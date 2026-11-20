import uuid
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

class User(AbstractBaseUser, PermissionsMixin):
    """
    Central User model representing all platform actors.
    Directly reflects the 'users' table in db/schema.sql.
    SRS: FR-1, FR-4, FR-34.
    """
    id = models.UUIDField(primary_key=True, default=generate_uuid, editable=False)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CLIENT)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    preferred_language = models.CharField(max_length=5, default='bn', choices=[('bn', 'Bangla'), ('en', 'English')])
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
    deleted_at = models.DateTimeField(null=True, blank=True)

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


class ClientProfile(models.Model):
    """
    Client profile model reflecting 'client_profiles' table in db/schema.sql.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        primary_key=True, 
        related_name='client_profile'
    )
    nid_number = models.CharField(max_length=30, blank=True, null=True)
    address = models.TextField(blank=True, default='')
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'client_profiles'
        verbose_name = 'Client Profile'
        verbose_name_plural = 'Client Profiles'

    def __str__(self):
        return f"Client: {self.user.full_name}"
