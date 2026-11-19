import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import UserManager

class UserRole(models.TextChoices):
    CLIENT = 'client', 'Client / General Public'
    LAWYER = 'lawyer', 'Lawyer / Advocate'
    ADMIN = 'admin', 'Platform Administrator'

class AccountStatus(models.TextChoices):
    INVITED = 'invited', 'Invited'
    PENDING_VERIFICATION = 'pending_verification', 'Pending Verification'
    ACTIVE = 'active', 'Active'
    SUSPENDED = 'suspended', 'Suspended'
    DEACTIVATED = 'deactivated', 'Deactivated'

class VerificationStatus(models.TextChoices):
    PENDING = 'pending', 'Pending Verification'
    APPROVED = 'approved', 'Approved & Verified'
    REJECTED = 'rejected', 'Verification Rejected'

class VerificationDocType(models.TextChoices):
    NID = 'nid', 'National Identification (NID)'
    BAR_CERTIFICATE = 'bar_certificate', 'Bangladesh Bar Council Certificate'

class User(AbstractBaseUser, PermissionsMixin):
    """
    Central user model representing all actors in LawAid (Clients, Lawyers, Admins).
    SRS: FR-1, FR-4, FR-34.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CLIENT)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    preferred_language = models.CharField(max_length=5, default='bn', choices=[('bn', 'Bangla'), ('en', 'English')])
    status = models.CharField(max_length=25, choices=AccountStatus.choices, default=AccountStatus.ACTIVE)
    avatar_url = models.URLField(max_length=500, null=True, blank=True)
    
    # Permissions & Auditing
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
        db_table = 'lawaid_users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.role}) - {self.email}"

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN or self.is_staff or self.is_superuser


class LawyerProfile(models.Model):
    """
    Lawyer Profile storing professional credentials and verification state.
    SRS: FR-2, FR-3, FR-6, FR-8, FR-38.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        primary_key=True, 
        related_name='lawyer_profile'
    )
    honorific = models.CharField(max_length=20, default='Adv.')
    headline = models.CharField(max_length=255, default='Advocate, High Court Division')
    bar_council_no = models.CharField(
        max_length=50, 
        unique=True, 
        db_index=True,
        help_text="Official Bar Council Sanad Number (e.g. SC-7841)"
    )
    bar_association = models.CharField(max_length=150, default='Dhaka Bar Association')
    chamber_address = models.TextField(blank=True, default='')
    district = models.CharField(max_length=100, default='Dhaka')
    years_experience = models.PositiveIntegerField(default=1)
    bio = models.TextField(blank=True, default='')
    specialization = models.CharField(max_length=255, default='Civil Litigation, Property Law')
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    session_minutes = models.PositiveSmallIntegerField(default=30)
    formats = models.CharField(max_length=100, default='video,audio,chat')
    offers_free_session = models.BooleanField(default=False)
    sos_available = models.BooleanField(default=False)

    # Verification status and badge attributes (FR-3)
    verification_status = models.CharField(
        max_length=20, 
        choices=VerificationStatus.choices, 
        default=VerificationStatus.PENDING,
        db_index=True
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='verified_lawyer_records'
    )
    rejection_reason = models.TextField(null=True, blank=True)

    # Ratings & Review counters
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    review_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lawaid_lawyer_profiles'
        verbose_name = 'Lawyer Profile'
        verbose_name_plural = 'Lawyer Profiles'

    def __str__(self):
        return f"{self.honorific} {self.user.full_name} [{self.bar_council_no}] - {self.verification_status}"

    @property
    def is_verified(self) -> bool:
        """Returns True ONLY when verification is approved by admin (FR-3)."""
        return self.verification_status == VerificationStatus.APPROVED

    def get_verification_badge(self):
        """
        Returns badge metadata ONLY after admin approval.
        Returns None if pending or rejected (FR-3).
        """
        if not self.is_verified:
            return None
            
        return {
            'is_active': True,
            'title': 'Bar Council Verified Advocate',
            'badge_name': 'LawAid Verified Seal',
            'sanad_number': self.bar_council_no,
            'bar_association': self.bar_association,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'verified_by_name': self.verified_by.full_name if self.verified_by else 'LawAid Compliance Admin',
            'trust_seal': 'Verified Credentials & Bangladesh Bar Council Sanad Authenticated',
        }


class LawyerVerificationDocument(models.Model):
    """
    Stores metadata for encrypted verification documents (NID card and Bar Council certificate).
    Actual raw files are stored ENCRYPTED on disk (AES-128-CBC + HMAC) and strictly admin-accessible.
    SRS: FR-2, NFR-4.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lawyer = models.ForeignKey(
        LawyerProfile, 
        on_delete=models.CASCADE, 
        related_name='verification_documents'
    )
    doc_type = models.CharField(
        max_length=25, 
        choices=VerificationDocType.choices,
        db_index=True
    )
    file_path = models.CharField(
        max_length=500, 
        help_text="Path to encrypted ciphertext file on server storage"
    )
    original_filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=100, default='application/pdf')
    file_size_bytes = models.PositiveIntegerField(default=0)
    sha256_checksum = models.CharField(max_length=64, blank=True, default='')

    status = models.CharField(
        max_length=20, 
        choices=VerificationStatus.choices, 
        default=VerificationStatus.PENDING
    )
    rejection_reason = models.TextField(null=True, blank=True)
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='reviewed_verification_documents'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'lawaid_lawyer_verification_documents'
        verbose_name = 'Lawyer Verification Document'
        verbose_name_plural = 'Lawyer Verification Documents'
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.get_doc_type_display()} for {self.lawyer.user.full_name} ({self.status})"


class ClientProfile(models.Model):
    """Client Profile for litigants/general public users."""
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
        db_table = 'lawaid_client_profiles'
        verbose_name = 'Client Profile'
        verbose_name_plural = 'Client Profiles'

    def __str__(self):
        return f"Client: {self.user.full_name}"
