from django.db.models import Q
from django.http import HttpResponse, Http404
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import (
    User, 
    LawyerProfile, 
    LawyerVerificationDocument, 
    VerificationStatus, 
    UserRole
)
from .serializers import (
    LawyerRegisterSerializer,
    LawyerSearchSerializer,
    LawyerProfileDetailSerializer,
    LawyerVerificationDocumentSerializer,
    VerificationRejectionSerializer,
)
from .permissions import IsPlatformAdmin, IsAdminOnlyForDocuments
from .encryption import DocumentEncryptionService

class LawyerRegisterView(APIView):
    """
    Lawyer Registration with mandatory NID and Bar Council certificate upload.
    Uploaded documents are immediately encrypted at rest using AES-128-CBC + HMAC.
    SRS: FR-1, FR-2, NFR-1, NFR-4.
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LawyerRegisterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            profile = serializer.save()
            return Response(
                {
                    'status': 'success',
                    'message': 'Lawyer registration submitted successfully. Your NID and Bar Council certificate have been securely encrypted and placed in the admin verification queue.',
                    'lawyer_id': str(profile.user.id),
                    'email': profile.user.email,
                    'bar_council_no': profile.bar_council_no,
                    'verification_status': profile.verification_status,
                    'is_verified': profile.is_verified,
                    'badge': profile.get_verification_badge(),
                    'notice': 'Your profile will remain hidden from client search results until verification is approved by a platform administrator (SRS FR-3).'
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LawyerSearchView(APIView):
    """
    Public Lawyer Search and Directory.
    
    SRS FR-3 / Schema v_lawyer_search:
    - Lawyers are HIDDEN from search until their verification status is 'approved'.
    - Unverified (pending or rejected) lawyers are strictly filtered out.
    - Verified lawyers display their official Verification Badge.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        # Base filter: ONLY approved lawyers (FR-3)
        queryset = LawyerProfile.objects.select_related('user').prefetch_related('verification_documents').filter(
            verification_status=VerificationStatus.APPROVED,
            user__is_active=True,
            user__deleted_at__isnull=True
        )

        # Allow platform administrators to inspect unverified lawyers if explicitly requested
        include_all = request.query_params.get('all', 'false').lower() == 'true'
        if include_all and request.user and request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_staff):
            queryset = LawyerProfile.objects.select_related('user').all()

        # Filters
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

        # Ordering
        ordering = request.query_params.get('ordering', '-avg_rating')
        if ordering in ['-avg_rating', 'consultation_fee', '-consultation_fee', '-years_experience']:
            queryset = queryset.order_by(ordering)

        serializer = LawyerSearchSerializer(queryset, many=True, context={'request': request})
        return Response({
            'count': len(serializer.data),
            'verified_only': not (include_all and request.user.is_authenticated and request.user.role == 'admin'),
            'results': serializer.data
        })


class LawyerProfileDetailView(APIView):
    """
    Retrieves a lawyer's public or private profile.
    - If verified: public can view profile with badge.
    - If unverified: hidden from public (returns 404). Only admin or the lawyer owner can view.
    SRS: FR-3, FR-8.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, lawyer_id, *args, **kwargs):
        try:
            profile = LawyerProfile.objects.select_related('user').get(user__id=lawyer_id)
        except LawyerProfile.DoesNotExist:
            raise Http404("Lawyer profile not found.")

        # Access check for unverified profiles
        user = request.user if request.user.is_authenticated else None
        is_admin = user and (user.role == 'admin' or user.is_staff or user.is_superuser)
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


class LawyerMyProfileView(APIView):
    """
    Enables authenticated lawyer to view their own profile and current verification status.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.role != UserRole.LAWYER:
            return Response({'error': 'Only lawyers have a lawyer profile.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            profile = request.user.lawyer_profile
        except LawyerProfile.DoesNotExist:
            raise Http404("Lawyer profile not found for this account.")
        serializer = LawyerProfileDetailSerializer(profile, context={'request': request})
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# ADMIN VERIFICATION MODULE (FR-38, NFR-4)
# ---------------------------------------------------------------------------

class AdminPendingVerificationsListView(APIView):
    """
    Admin-only endpoint listing all lawyer verification requests.
    SRS: FR-38.
    """
    permission_classes = [IsPlatformAdmin]

    def get(self, request, *args, **kwargs):
        status_filter = request.query_params.get('status', VerificationStatus.PENDING)
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


class AdminVerificationDetailView(APIView):
    """
    Admin-only endpoint to inspect full details of a single lawyer's application.
    """
    permission_classes = [IsPlatformAdmin]

    def get(self, request, lawyer_id, *args, **kwargs):
        try:
            profile = LawyerProfile.objects.select_related('user').prefetch_related('verification_documents').get(user__id=lawyer_id)
        except LawyerProfile.DoesNotExist:
            raise Http404("Lawyer application not found.")

        serializer = LawyerProfileDetailSerializer(profile, context={'request': request})
        return Response(serializer.data)


class AdminApproveVerificationView(APIView):
    """
    Admin-only action: Approves lawyer's verification request.
    - Sets verification_status = 'approved'
    - Records verified_at timestamp and admin identifier
    - Automatically enables the Verification Badge (FR-3)
    - Makes the lawyer visible in search results (FR-3)
    """
    permission_classes = [IsPlatformAdmin]

    def post(self, request, lawyer_id, *args, **kwargs):
        try:
            profile = LawyerProfile.objects.get(user__id=lawyer_id)
        except LawyerProfile.DoesNotExist:
            raise Http404("Lawyer not found.")

        profile.verification_status = VerificationStatus.APPROVED
        profile.verified_at = timezone.now()
        profile.verified_by = request.user
        profile.rejection_reason = None
        profile.save()

        # Update all attached verification documents to approved
        profile.verification_documents.all().update(
            status=VerificationStatus.APPROVED,
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
            rejection_reason=None
        )

        return Response({
            'status': 'success',
            'message': f"Lawyer {profile.user.full_name} ({profile.bar_council_no}) has been approved.",
            'lawyer_id': str(profile.user.id),
            'verification_status': profile.verification_status,
            'is_verified': profile.is_verified,
            'badge': profile.get_verification_badge(),
        })


class AdminRejectVerificationView(APIView):
    """
    Admin-only action: Rejects lawyer's verification request with mandatory reason.
    - Sets verification_status = 'rejected'
    - Records rejection reason
    - Keeps lawyer hidden from public search and without verification badge.
    """
    permission_classes = [IsPlatformAdmin]

    def post(self, request, lawyer_id, *args, **kwargs):
        try:
            profile = LawyerProfile.objects.get(user__id=lawyer_id)
        except LawyerProfile.DoesNotExist:
            raise Http404("Lawyer not found.")

        serializer = VerificationRejectionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        reason = serializer.validated_data['rejection_reason']
        profile.verification_status = VerificationStatus.REJECTED
        profile.rejection_reason = reason
        profile.verified_by = request.user
        profile.save()

        # Update documents to rejected
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
            'badge': profile.get_verification_badge(),  # None
        })


class AdminDocumentDecryptionView(APIView):
    """
    Secure Admin-Only Document Viewing & Download.
    
    SRS NFR-4:
    'The system shall never expose a client's or lawyer's uploaded identification documents 
    (NID, Bar Council certificate) to any party other than platform administrators during verification.'
    
    - Reads the encrypted file from storage.
    - Decrypts the raw ciphertext in-memory via DocumentEncryptionService.
    - Streams decrypted bytes directly to the authenticated administrator.
    - All non-admins receive a strict 403 Forbidden.
    """
    permission_classes = [IsAdminOnlyForDocuments]

    def get(self, request, document_id, action='view', *args, **kwargs):
        try:
            doc = LawyerVerificationDocument.objects.select_related('lawyer__user').get(id=document_id)
        except LawyerVerificationDocument.DoesNotExist:
            raise Http404("Document record not found.")

        try:
            decrypted_bytes = DocumentEncryptionService.read_and_decrypt_file(doc.file_path)
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


class AdminVerificationOverviewStatsView(APIView):
    """
    Overview statistics for the Admin Verification panel (mirrors v_admin_overview).
    """
    permission_classes = [IsPlatformAdmin]

    def get(self, request, *args, **kwargs):
        total_lawyers = LawyerProfile.objects.count()
        pending = LawyerProfile.objects.filter(verification_status=VerificationStatus.PENDING).count()
        approved = LawyerProfile.objects.filter(verification_status=VerificationStatus.APPROVED).count()
        rejected = LawyerProfile.objects.filter(verification_status=VerificationStatus.REJECTED).count()

        return Response({
            'total_registered_lawyers': total_lawyers,
            'pending_verifications': pending,
            'verified_lawyers': approved,
            'rejected_verifications': rejected,
            'approval_rate_percent': round((approved / total_lawyers * 100), 1) if total_lawyers > 0 else 0,
        })
