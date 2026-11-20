from rest_framework import serializers
from .models import LawyerProfile, LawyerVerificationDocument, Court, PracticeArea

class LawyerVerificationDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for encrypted verification documents.
    Does not expose server disk paths directly (NFR-4).
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
            'status',
            'rejection_reason',
            'submitted_at',
            'reviewed_at',
            'view_url',
            'download_url',
        ]

    def get_view_url(self, obj):
        request = self.context.get('request')
        url = f"/api/lawyers/verification/documents/{obj.id}/view/"
        return request.build_absolute_uri(url) if request else url

    def get_download_url(self, obj):
        request = self.context.get('request')
        url = f"/api/lawyers/verification/documents/{obj.id}/download/"
        return request.build_absolute_uri(url) if request else url


class LawyerSearchSerializer(serializers.ModelSerializer):
    """
    Public Lawyer Search Serializer.
    Only approved lawyers are returned in public searches (FR-3).
    Displays the verified badge when verification is approved.
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
    Detailed lawyer profile serializer.
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

        # Expose uploaded documents ONLY to platform admins or the lawyer themselves
        if user and user.is_authenticated and (user.is_staff or getattr(user, 'role', '') == 'admin' or user.id == obj.user.id):
            docs = obj.verification_documents.all()
            return LawyerVerificationDocumentSerializer(docs, many=True, context=self.context).data
        return []


class VerificationRejectionSerializer(serializers.Serializer):
    """Rejects lawyer verification with required rejection reason."""
    rejection_reason = serializers.CharField(required=True, min_length=5)
