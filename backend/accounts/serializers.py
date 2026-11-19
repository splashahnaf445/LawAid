from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from .models import (
    User, 
    LawyerProfile, 
    LawyerVerificationDocument, 
    UserRole, 
    VerificationStatus, 
    VerificationDocType
)
from .validators import (
    validate_bd_phone, 
    validate_bar_council_no, 
    validate_verification_document,
    normalize_bd_phone
)
from .encryption import DocumentEncryptionService

class LawyerVerificationDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for verification document metadata.
    Does NOT expose raw server file paths (NFR-4).
    """
    view_url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = LawyerVerificationDocument
        fields = [
            'id',
            'doc_type',
            'original_filename',
            'mime_type',
            'file_size_bytes',
            'sha256_checksum',
            'status',
            'rejection_reason',
            'submitted_at',
            'reviewed_at',
            'view_url',
            'download_url',
        ]

    def get_view_url(self, obj):
        request = self.context.get('request')
        url = f"/api/verification/documents/{obj.id}/view/"
        return request.build_absolute_uri(url) if request else url

    def get_download_url(self, obj):
        request = self.context.get('request')
        url = f"/api/verification/documents/{obj.id}/download/"
        return request.build_absolute_uri(url) if request else url


class LawyerRegisterSerializer(serializers.Serializer):
    """
    Serializer for Lawyer Registration with mandatory encrypted document upload.
    SRS: FR-1, FR-2, NFR-1, NFR-4.
    """
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=6)
    
    # Lawyer profile fields
    honorific = serializers.CharField(max_length=20, default='Adv.')
    headline = serializers.CharField(max_length=255, default='Advocate, High Court Division')
    bar_council_no = serializers.CharField(max_length=50)
    bar_association = serializers.CharField(max_length=150, default='Dhaka Bar Association')
    chamber_address = serializers.CharField(required=False, allow_blank=True, default='')
    district = serializers.CharField(max_length=100, default='Dhaka')
    specialization = serializers.CharField(max_length=255, default='Civil Litigation, Property Law')
    consultation_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    years_experience = serializers.IntegerField(default=1, min_value=0)
    bio = serializers.CharField(required=False, allow_blank=True, default='')

    # Uploaded verification documents (FR-2)
    nid_document = serializers.FileField(write_only=True)
    bar_certificate_document = serializers.FileField(write_only=True)

    def validate_email(self, value):
        normalized = value.strip().lower()
        if User.objects.filter(email=normalized).exists():
            raise serializers.ValidationError("A user with this email address already exists.")
        return normalized

    def validate_phone(self, value):
        if not value:
            return None
        normalized = normalize_bd_phone(value)
        validate_bd_phone(normalized)
        if User.objects.filter(phone=normalized).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return normalized

    def validate_bar_council_no(self, value):
        cleaned = value.strip().upper()
        validate_bar_council_no(cleaned)
        if LawyerProfile.objects.filter(bar_council_no=cleaned).exists():
            raise serializers.ValidationError("A lawyer with this Bar Council Sanad Number is already registered.")
        return cleaned

    def validate_nid_document(self, value):
        validate_verification_document(value)
        return value

    def validate_bar_certificate_document(self, value):
        validate_verification_document(value)
        return value

    @transaction.atomic
    def create(self, validated_data):
        nid_doc = validated_data.pop('nid_document')
        bar_cert_doc = validated_data.pop('bar_certificate_document')
        password = validated_data.pop('password')
        
        # User account creation
        user = User.objects.create_user(
            email=validated_data.pop('email'),
            full_name=validated_data.pop('full_name'),
            phone=validated_data.pop('phone', None),
            password=password,
            role=UserRole.LAWYER,
            status='active'
        )

        # Profile creation with initial 'pending' status
        profile = LawyerProfile.objects.create(
            user=user,
            verification_status=VerificationStatus.PENDING,
            **validated_data
        )

        # Encrypt and store NID Document (FR-2, NFR-1, NFR-4)
        nid_saved = DocumentEncryptionService.save_encrypted_file(
            uploaded_file=nid_doc,
            lawyer_id=str(user.id),
            doc_type=VerificationDocType.NID
        )
        LawyerVerificationDocument.objects.create(
            lawyer=profile,
            doc_type=VerificationDocType.NID,
            file_path=nid_saved['file_path'],
            original_filename=nid_saved['original_filename'],
            mime_type=nid_saved['mime_type'],
            file_size_bytes=nid_saved['file_size_bytes'],
            sha256_checksum=nid_saved['sha256_checksum'],
            status=VerificationStatus.PENDING
        )

        # Encrypt and store Bar Council Certificate (FR-2, NFR-1, NFR-4)
        bar_saved = DocumentEncryptionService.save_encrypted_file(
            uploaded_file=bar_cert_doc,
            lawyer_id=str(user.id),
            doc_type=VerificationDocType.BAR_CERTIFICATE
        )
        LawyerVerificationDocument.objects.create(
            lawyer=profile,
            doc_type=VerificationDocType.BAR_CERTIFICATE,
            file_path=bar_saved['file_path'],
            original_filename=bar_saved['original_filename'],
            mime_type=bar_saved['mime_type'],
            file_size_bytes=bar_saved['file_size_bytes'],
            sha256_checksum=bar_saved['sha256_checksum'],
            status=VerificationStatus.PENDING
        )

        return profile


class LawyerSearchSerializer(serializers.ModelSerializer):
    """
    Public lawyer search representation.
    Only approved lawyers appear in search results (FR-3).
    Includes the verification badge if approved.
    """
    lawyer_id = serializers.UUIDField(source='user.id', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    avatar_url = serializers.CharField(source='user.avatar_url', read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    verification_badge = serializers.SerializerMethodField()

    class Meta:
        model = LawyerProfile
        fields = [
            'lawyer_id',
            'full_name',
            'email',
            'phone',
            'avatar_url',
            'honorific',
            'headline',
            'bar_council_no',
            'bar_association',
            'district',
            'specialization',
            'consultation_fee',
            'years_experience',
            'avg_rating',
            'review_count',
            'verification_status',
            'is_verified',
            'verification_badge',
        ]

    def get_verification_badge(self, obj):
        return obj.get_verification_badge()


class LawyerProfileDetailSerializer(serializers.ModelSerializer):
    """
    Detailed profile serializer for public view or lawyer/admin view.
    """
    lawyer_id = serializers.UUIDField(source='user.id', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    avatar_url = serializers.CharField(source='user.avatar_url', read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    verification_badge = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()

    class Meta:
        model = LawyerProfile
        fields = [
            'lawyer_id',
            'full_name',
            'email',
            'phone',
            'avatar_url',
            'honorific',
            'headline',
            'bar_council_no',
            'bar_association',
            'chamber_address',
            'district',
            'years_experience',
            'bio',
            'specialization',
            'consultation_fee',
            'session_minutes',
            'formats',
            'offers_free_session',
            'sos_available',
            'verification_status',
            'verified_at',
            'rejection_reason',
            'avg_rating',
            'review_count',
            'is_verified',
            'verification_badge',
            'documents',
        ]

    def get_verification_badge(self, obj):
        return obj.get_verification_badge()

    def get_documents(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        
        # Only expose document metadata to admins or the lawyer themselves
        if user and user.is_authenticated and (user.role == 'admin' or user.is_staff or user.id == obj.user.id):
            docs = obj.verification_documents.all()
            return LawyerVerificationDocumentSerializer(docs, many=True, context=self.context).data
        return []


class VerificationApprovalSerializer(serializers.Serializer):
    """Approves a lawyer's verification request."""
    pass


class VerificationRejectionSerializer(serializers.Serializer):
    """Rejects a lawyer's verification request with mandatory reason."""
    rejection_reason = serializers.CharField(required=True, min_length=5)
