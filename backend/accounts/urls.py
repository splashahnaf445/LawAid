from django.urls import path
from .views import (
    LawyerRegisterView,
    LawyerSearchView,
    LawyerProfileDetailView,
    LawyerMyProfileView,
    AdminPendingVerificationsListView,
    AdminVerificationDetailView,
    AdminApproveVerificationView,
    AdminRejectVerificationView,
    AdminDocumentDecryptionView,
    AdminVerificationOverviewStatsView,
)

urlpatterns = [
    # Registration (FR-1, FR-2)
    path('auth/register/lawyer/', LawyerRegisterView.as_view(), name='register-lawyer'),
    
    # Lawyer Directory & Public Profiles (FR-3, FR-6, FR-8)
    path('lawyers/', LawyerSearchView.as_view(), name='lawyer-search'),
    path('lawyers/me/', LawyerMyProfileView.as_view(), name='lawyer-my-profile'),
    path('lawyers/<uuid:lawyer_id>/', LawyerProfileDetailView.as_view(), name='lawyer-profile-detail'),

    # Admin Verification & Compliance Operations (FR-3, FR-38, NFR-4)
    path('verification/stats/', AdminVerificationOverviewStatsView.as_view(), name='admin-verification-stats'),
    path('verification/pending-lawyers/', AdminPendingVerificationsListView.as_view(), name='admin-pending-lawyers'),
    path('verification/lawyers/<uuid:lawyer_id>/', AdminVerificationDetailView.as_view(), name='admin-lawyer-detail'),
    path('verification/lawyers/<uuid:lawyer_id>/approve/', AdminApproveVerificationView.as_view(), name='admin-approve-lawyer'),
    path('verification/lawyers/<uuid:lawyer_id>/reject/', AdminRejectVerificationView.as_view(), name='admin-reject-lawyer'),
    
    # Encrypted Document Retrieval (NFR-4: Admin Only)
    path('verification/documents/<uuid:document_id>/view/', AdminDocumentDecryptionView.as_view(), {'action': 'view'}, name='admin-view-doc'),
    path('verification/documents/<uuid:document_id>/download/', AdminDocumentDecryptionView.as_view(), {'action': 'download'}, name='admin-download-doc'),
]
