from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import transaction
from core.encryption import DocumentEncryptionService
from .models import User, ClientProfile, UserRole, AccountStatus
from .validators import validate_bd_phone, validate_bar_council_no, validate_verification_document, normalize_bd_phone
from lawyers.models import LawyerProfile, LawyerVerificationDocument, VerificationStatus, VerificationDocType

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Returns user payload along with JWT tokens for frontend session management.
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

class ClientRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    address = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'password', 'address']

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

    @transaction.atomic
    def create(self, validated_data):
        address = validated_data.pop('address', '')
        password = validated_data.pop('password')
        user = User.objects.create_user(
            password=password,
            role=UserRole.CLIENT,
            status=AccountStatus.ACTIVE,
            **validated_data
        )
        ClientProfile.objects.create(user=user, address=address)
        return user


class LawyerRegisterSerializer(serializers.Serializer):
    """
    Lawyer Registration with mandatory NID and Bar Council certificate upload.
    Files are encrypted upon ingestion using authenticated AES-128-CBC + HMAC.
    SRS: FR-1, FR-2, NFR-1, NFR-4.
    """
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=6)

    # Lawyer credentials
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

        # 1. Create User account with role 'lawyer'
        user = User.objects.create_user(
            email=validated_data.pop('email'),
            full_name=validated_data.pop('full_name'),
            phone=validated_data.pop('phone', None),
            password=password,
            role=UserRole.LAWYER,
            status=AccountStatus.ACTIVE
        )

        # 2. Create LawyerProfile with status 'pending'
        profile = LawyerProfile.objects.create(
            user=user,
            verification_status=VerificationStatus.PENDING,
            **validated_data
        )

        # 3. Encrypt and save NID document (FR-2, NFR-1, NFR-4)
        nid_saved = DocumentEncryptionService.save_encrypted_file(
            uploaded_file=nid_doc,
            lawyer_id=str(user.id),
            doc_type=VerificationDocType.NID
        )
        LawyerVerificationDocument.objects.create(
            lawyer=profile,
            doc_type=VerificationDocType.NID,
            file_url=nid_saved['file_url'],
            original_filename=nid_saved['original_filename'],
            mime_type=nid_saved['mime_type'],
            file_size_bytes=nid_saved['file_size_bytes'],
            status=VerificationStatus.PENDING
        )

        # 4. Encrypt and save Bar Council Certificate (FR-2, NFR-1, NFR-4)
        bar_saved = DocumentEncryptionService.save_encrypted_file(
            uploaded_file=bar_cert_doc,
            lawyer_id=str(user.id),
            doc_type=VerificationDocType.BAR_CERTIFICATE
        )
        LawyerVerificationDocument.objects.create(
            lawyer=profile,
            doc_type=VerificationDocType.BAR_CERTIFICATE,
            file_url=bar_saved['file_url'],
            original_filename=bar_saved['original_filename'],
            mime_type=bar_saved['mime_type'],
            file_size_bytes=bar_saved['file_size_bytes'],
            status=VerificationStatus.PENDING
        )

        return profile
