from django.urls import path
from .views import (
    LawyerSearchView,
    LawyerProfileDetailView,
    AdminVerificationQueueView,
    AdminApproveLawyerView,
    AdminRejectLawyerView,
    AdminDocumentDecryptionView,
)

urlpatterns = [
    # Public Lawyer Directory & Profiles (FR-3, FR-6, FR-8)
    path('', LawyerSearchView.as_view(), name='lawyer-search'),
    path('<uuid:lawyer_id>/', LawyerProfileDetailView.as_view(), name='lawyer-detail'),

    # Admin Compliance Verification Queue & Actions (FR-3, FR-38)
    path('verification/queue/', AdminVerificationQueueView.as_view(), name='admin-verification-queue'),
    path('verification/<uuid:lawyer_id>/approve/', AdminApproveLawyerView.as_view(), name='admin-approve-lawyer'),
    path('verification/<uuid:lawyer_id>/reject/', AdminRejectLawyerView.as_view(), name='admin-reject-lawyer'),

    # Encrypted Document In-Memory Decryption Stream (NFR-4: Admin Only)
    path('verification/documents/<uuid:document_id>/view/', AdminDocumentDecryptionView.as_view(), {'action': 'view'}, name='admin-view-document'),
    path('verification/documents/<uuid:document_id>/download/', AdminDocumentDecryptionView.as_view(), {'action': 'download'}, name='admin-download-document'),
]
