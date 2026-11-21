from django.db.models import Q
from django.http import HttpResponse, Http404
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from accounts.models import AccountStatus
from core.permissions import IsPlatformAdmin, IsAdminOnlyForDocuments
from core.encryption import DocumentEncryptionService
from .models import Court, LawyerProfile, LawyerVerificationDocument, PracticeArea, VerificationStatus
from .serializers import (
    CourtSerializer,
    LawyerSearchSerializer,
    LawyerProfileDetailSerializer,
    LawyerVerificationDocumentSerializer,
    PracticeAreaSerializer,
    VerificationRejectionSerializer
)

class LawyerSearchView(APIView):
    """
    Public Lawyer Search and Discovery.
    
    SRS FR-3:
    - Lawyers are HIDDEN from search until their verification status is 'approved'.
    - Unverified (pending or rejected) lawyers are strictly filtered out.
    - Verified lawyers display their official Verification Badge.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        # Base filter: strictly approved lawyers (FR-3)
        queryset = LawyerProfile.objects.select_related('user').filter(
            verification_status=VerificationStatus.APPROVED,
            user__is_active=True,
            user__deleted_at__isnull=True
        )

        # Allow platform compliance admins to inspect unverified lawyers if explicitly requested
        include_all = request.query_params.get('all', 'false').lower() == 'true'
        user = request.user
        if include_all and user and user.is_authenticated and (getattr(user, 'role', '') == 'admin' or user.is_staff):
            queryset = LawyerProfile.objects.select_related('user').all()

        query = request.query_params.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(user__full_name__icontains=query) |
                Q(headline__icontains=query) |
                Q(specialization__icontains=query) |
                Q(bar_council_no__icontains=query) |
                Q(district__icontains=query)
            )

        district = request.query_params.get('district', '').strip()
        if district:
            queryset = queryset.filter(district__iexact=district)

        specialization = request.query_params.get('specialization', '').strip()
        if specialization:
            queryset = queryset.filter(specialization__icontains=specialization)

        # Filters the frontend (src/api/lawyers.js) sends: court name, practice-area slug/name.
        court = request.query_params.get('court', '').strip()
        if court:
            queryset = queryset.filter(primary_court__name__icontains=court)

        practice_area = request.query_params.get('practice_area', '').strip()
        if practice_area:
            queryset = queryset.filter(
                Q(practice_areas__slug__iexact=practice_area) |
                Q(practice_areas__name_en__icontains=practice_area)
            ).distinct()

        serializer = LawyerSearchSerializer(queryset, many=True, context={'request': request})
        return Response({
            'count': len(serializer.data),
            'verified_only': not (include_all and user.is_authenticated and getattr(user, 'role', '') == 'admin'),
            'results': serializer.data
        })


class LawyerProfileDetailView(APIView):
    """
    Detailed Profile View for a Lawyer.
    SRS FR-3, FR-8:
    - Approved lawyer profiles are publicly accessible and feature the official verified badge.
    - Unverified lawyer profiles are hidden from public view (returns 404). Only admin or the lawyer owner can access.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, lawyer_id, *args, **kwargs):
        try:
            profile = LawyerProfile.objects.select_related('user').get(user__id=lawyer_id)
        except LawyerProfile.DoesNotExist:
            raise Http404("Lawyer profile not found.")

        user = request.user if request.user.is_authenticated else None
        is_admin = user and (getattr(user, 'role', '') == 'admin' or user.is_staff or user.is_superuser)
        is_owner = user and user.id == profile.user.id

        if profile.verification_status != VerificationStatus.APPROVED and not (is_admin or is_owner):
            return Response(
                {
                    'error': 'This lawyer profile is currently pending verification and is hidden from public view (SRS FR-3).'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = LawyerProfileDetailSerializer(profile, context={'request': request})
        return Response(serializer.data)


# ---------------------------------------------------------------------
# Admin Verification & Document Decryption (FR-3, FR-38, NFR-4)
# ---------------------------------------------------------------------

class AdminVerificationQueueView(APIView):
    """
    Admin-only review queue of lawyer applications.
    SRS FR-38.
    """
    permission_classes = [IsPlatformAdmin]

    def get(self, request, *args, **kwargs):
        status_filter = request.query_params.get('status', 'pending')
        queryset = LawyerProfile.objects.select_related('user').prefetch_related('verification_documents')

        if status_filter != 'all':
            queryset = queryset.filter(verification_status=status_filter)

        queryset = queryset.order_by('-created_at')

        data = []
        for lp in queryset:
            docs = lp.verification_documents.all()
            doc_data = LawyerVerificationDocumentSerializer(docs, many=True, context={'request': request}).data
            data.append({
                'lawyer_id': str(lp.user.id),
                'full_name': lp.user.full_name,
                'email': lp.user.email,
                'phone': lp.user.phone,
                'honorific': lp.honorific,
                'headline': lp.headline,
                'bar_council_no': lp.bar_council_no,
                'bar_association': lp.bar_association,
                'district': lp.district,
                'specialization': lp.specialization,
                'years_experience': lp.years_experience,
                'verification_status': lp.verification_status,
                'verified_at': lp.verified_at,
                'rejection_reason': lp.rejection_reason,
                'submitted_at': lp.created_at,
                'documents': doc_data,
            })

        return Response({
            'count': len(data),
            'filter': status_filter,
            'applications': data
        })


class AdminApproveLawyerView(APIView):
    """
    Admin approves lawyer credentials (FR-3, FR-38).
    - Updates verification_status = 'approved'
    - Stamps verified_at and verified_by
    - Activates the official Verification Badge
    - Reveals the lawyer in public searches
    """
    permission_classes = [IsPlatformAdmin]

    def post(self, request, lawyer_id, *args, **kwargs):
        try:
            profile = LawyerProfile.objects.get(user__id=lawyer_id)
        except LawyerProfile.DoesNotExist:
            raise Http404("Lawyer application not found.")

        profile.verification_status = VerificationStatus.APPROVED
        profile.verified_at = timezone.now()
        profile.verified_by = request.user
        profile.rejection_reason = None
        profile.save()

        # Integration: registration (Usama, SYS-18) creates lawyers with account status
        # 'pending_verification'; approval makes the account active, as in db/seed.sql.
        if profile.user.status == AccountStatus.PENDING_VERIFICATION:
            profile.user.status = AccountStatus.ACTIVE
            profile.user.save(update_fields=['status', 'updated_at'])

        # Mark all verification documents as approved
        profile.verification_documents.all().update(
            status=VerificationStatus.APPROVED,
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
            rejection_reason=None
        )

        return Response({
            'status': 'success',
            'message': f"Lawyer {profile.user.full_name} ({profile.bar_council_no}) approved.",
            'lawyer_id': str(profile.user.id),
            'verification_status': profile.verification_status,
            'is_verified': profile.is_verified,
            'badge': profile.get_verification_badge(),
        })


class AdminRejectLawyerView(APIView):
    """
    Admin rejects lawyer credentials with mandatory rejection reason (FR-38).
    - Updates verification_status = 'rejected'
    - Lawyer remains unbadged and hidden from public search
    """
    permission_classes = [IsPlatformAdmin]

    def post(self, request, lawyer_id, *args, **kwargs):
        try:
            profile = LawyerProfile.objects.get(user__id=lawyer_id)
        except LawyerProfile.DoesNotExist:
            raise Http404("Lawyer application not found.")

        serializer = VerificationRejectionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        reason = serializer.validated_data['rejection_reason']
        profile.verification_status = VerificationStatus.REJECTED
        profile.rejection_reason = reason
        profile.verified_by = request.user
        profile.save()

        profile.verification_documents.all().update(
            status=VerificationStatus.REJECTED,
            rejection_reason=reason,
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )

        return Response({
            'status': 'rejected',
            'message': f"Lawyer {profile.user.full_name} verification was rejected.",
            'lawyer_id': str(profile.user.id),
            'verification_status': profile.verification_status,
            'is_verified': profile.is_verified,
            'rejection_reason': reason,
            'badge': profile.get_verification_badge(),
        })


class AdminDocumentDecryptionView(APIView):
    """
    Secure In-Memory Document Decryption Stream.
    
    SRS NFR-4:
    'The system shall never expose a client's or lawyer's uploaded identification documents 
    (NID, Bar Council certificate) to any party other than platform administrators during verification.'
    
    - Reads the encrypted ciphertext from disk.
    - Decrypts raw content in-memory via DocumentEncryptionService.
    - Streams decrypted bytes with proper MIME type directly to the authenticated administrator.
    - Non-admins strictly receive 403 Forbidden.
    """
    permission_classes = [IsAdminOnlyForDocuments]

    def get(self, request, document_id, action='view', *args, **kwargs):
        try:
            doc = LawyerVerificationDocument.objects.select_related('lawyer__user').get(id=document_id)
        except LawyerVerificationDocument.DoesNotExist:
            raise Http404("Document record not found.")

        try:
            decrypted_bytes = DocumentEncryptionService.read_and_decrypt_file(doc.file_url)
        except Exception as exc:
            return Response(
                {'error': f"Failed to decrypt document: {str(exc)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        response = HttpResponse(decrypted_bytes, content_type=doc.mime_type)
        disposition = 'attachment' if action == 'download' else 'inline'
        response['Content-Disposition'] = f'{disposition}; filename="{doc.original_filename}"'
        response['X-Content-Type-Options'] = 'nosniff'
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
        return response


# ---------------------------------------------------------------------------
# Usama (SYS-18): reference data for the registration dropdowns
# (mounted at /api/reference/ - see lawyers/reference_urls.py)
# ---------------------------------------------------------------------------
class _PublicList(ListAPIView):
    """Reference data for the registration dropdowns - public, unpaginated."""

    permission_classes = [AllowAny]
    authentication_classes = []
    pagination_class = None


class CourtListView(_PublicList):
    queryset = Court.objects.all()
    serializer_class = CourtSerializer


class PracticeAreaListView(_PublicList):
    queryset = PracticeArea.objects.all()
    serializer_class = PracticeAreaSerializer
