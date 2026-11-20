import uuid
from django.db import models
from core.ids import generate_uuid
from accounts.models import User

class VerificationStatus(models.TextChoices):
    PENDING = 'pending', 'Pending Verification'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'

class VerificationDocType(models.TextChoices):
    NID = 'nid', 'National ID Card'
    BAR_CERTIFICATE = 'bar_certificate', 'Bar Council Certificate'

class Court(models.Model):
    name = models.CharField(max_length=255, unique=True)
    court_type = models.CharField(max_length=100)
    district = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'courts'

    def __str__(self):
        return self.name

class PracticeArea(models.Model):
    slug = models.SlugField(max_length=100, unique=True)
    name_en = models.CharField(max_length=150)
    name_bn = models.CharField(max_length=150)

    class Meta:
        db_table = 'practice_areas'

    def __str__(self):
        return self.name_en

class LawyerProfile(models.Model):
    """
    Lawyer profile model directly mapping to 'lawyer_profiles' table in db/schema.sql.
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
    bar_council_no = models.CharField(max_length=50, unique=True, db_index=True)
    bar_association = models.CharField(max_length=150, default='Dhaka Bar Association')
    primary_court = models.ForeignKey(Court, null=True, blank=True, on_delete=models.SET_NULL)
    chamber_address = models.TextField(blank=True, default='')
    district = models.CharField(max_length=100, default='Dhaka')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
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
        related_name='verified_lawyers'
    )
    rejection_reason = models.TextField(null=True, blank=True)

    # Ratings
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    review_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lawyer_profiles'
        verbose_name = 'Lawyer Profile'
        verbose_name_plural = 'Lawyer Profiles'

    def __str__(self):
        return f"{self.honorific} {self.user.full_name} [{self.bar_council_no}] - {self.verification_status}"

    @property
    def is_verified(self) -> bool:
        """Returns True ONLY after admin approval (FR-3)."""
        return self.verification_status == VerificationStatus.APPROVED

    def get_verification_badge(self):
        """
        SRS FR-3: Show verification badge on lawyer profile only after admin approval.
        Returns badge metadata dictionary if approved, None if pending or rejected.
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
    Stores metadata for encrypted verification documents.
    Physical files are stored ENCRYPTED on disk (NFR-4) and strictly accessible to admins.
    SRS: FR-2, NFR-4.
    """
    id = models.UUIDField(primary_key=True, default=generate_uuid, editable=False)
    lawyer = models.ForeignKey(
        LawyerProfile, 
        on_delete=models.CASCADE, 
        related_name='verification_documents'
    )
    doc_type = models.CharField(max_length=25, choices=VerificationDocType.choices, db_index=True)
    file_url = models.CharField(max_length=500, help_text="Path or private URL to encrypted ciphertext file")
    status = models.CharField(max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.PENDING)
    rejection_reason = models.TextField(null=True, blank=True)
    
    # Audit fields
    original_filename = models.CharField(max_length=255, default='')
    mime_type = models.CharField(max_length=100, default='application/pdf')
    file_size_bytes = models.PositiveIntegerField(default=0)
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='reviewed_documents'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'lawyer_verification_documents'
        verbose_name = 'Lawyer Verification Document'
        verbose_name_plural = 'Lawyer Verification Documents'
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.doc_type} for {self.lawyer.user.full_name} ({self.status})"
