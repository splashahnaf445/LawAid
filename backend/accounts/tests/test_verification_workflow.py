import shutil
import tempfile
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import User, LawyerProfile, LawyerVerificationDocument, VerificationStatus

class LawyerVerificationWorkflowTestCase(TestCase):
    """
    Integration tests for Lawyer registration, document upload, admin approval, and rejection.
    SRS Compliance:
    - FR-2: Mandatory NID & Bar Council Certificate upload during registration.
    - FR-3: Verification status and badge logic (badge granted upon approval).
    - FR-38: Admin verification review, approval, and rejection.
    """
    def setUp(self):
        self.client = APIClient()
        self.temp_storage_dir = tempfile.mkdtemp()

        # Admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@lawaid.gov.bd',
            full_name='Lead Administrator Rahid Karim',
            password='AdminPassword123'
        )

        # Standard client user
        self.regular_client = User.objects.create_user(
            email='client@example.com',
            full_name='General Client Nafseen',
            password='ClientPassword123',
            role='client'
        )

    def tearDown(self):
        shutil.rmtree(self.temp_storage_dir, ignore_errors=True)

    def test_lawyer_registration_with_documents(self):
        """Lawyer registers with NID & Bar Council Certificate; gets 'pending' status."""
        url = reverse('register-lawyer')

        nid_file = SimpleUploadedFile(
            "nid_sample.pdf",
            b"%PDF-1.4 National Identity Document 1988269041200021",
            content_type="application/pdf"
        )
        bar_cert_file = SimpleUploadedFile(
            "bar_cert.png",
            b"\x89PNG\r\n\x1a\nBar Council Sanad SC-7841 Certificate",
            content_type="image/png"
        )

        payload = {
            'full_name': 'Adv. Rezwan Hossain',
            'email': 'adv.rezwan@apexlegal.bd',
            'password': 'LawyerPass123!',
            'phone': '+8801712345678',
            'honorific': 'Adv.',
            'headline': 'Senior Advocate, High Court Division',
            'bar_council_no': 'SC-7841',
            'bar_association': 'Supreme Court Bar Association',
            'district': 'Dhaka',
            'specialization': 'Civil Litigation, Writ Petition',
            'consultation_fee': '1500.00',
            'years_experience': 12,
            'bio': '12+ years experience in the Supreme Court of Bangladesh.',
            'nid_document': nid_file,
            'bar_certificate_document': bar_cert_file,
        }

        with override_settings(ENCRYPTED_DOCUMENTS_DIR=self.temp_storage_dir):
            response = self.client.post(url, payload, format='multipart')

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['status'], 'success')
            self.assertEqual(response.data['verification_status'], VerificationStatus.PENDING)
            self.assertFalse(response.data['is_verified'])
            self.assertIsNone(response.data['badge'])

            # Verify database state
            profile = LawyerProfile.objects.get(bar_council_no='SC-7841')
            self.assertEqual(profile.verification_status, VerificationStatus.PENDING)
            self.assertFalse(profile.is_verified)
            self.assertIsNone(profile.get_verification_badge())

            # Check that two encrypted documents were created
            docs = profile.verification_documents.all()
            self.assertEqual(docs.count(), 2)
            doc_types = {d.doc_type for d in docs}
            self.assertEqual(doc_types, {'nid', 'bar_certificate'})

    def test_admin_approve_lawyer_enables_badge(self):
        """Admin approves lawyer; verification_status becomes 'approved' and badge is enabled."""
        with override_settings(ENCRYPTED_DOCUMENTS_DIR=self.temp_storage_dir):
            # Create a pending lawyer
            lawyer_user = User.objects.create_user(
                email='lawyer.test@bar.bd',
                full_name='Adv. Syed Farhan',
                password='Password123',
                role='lawyer'
            )
            profile = LawyerProfile.objects.create(
                user=lawyer_user,
                bar_council_no='DH-9921',
                verification_status=VerificationStatus.PENDING
            )

            # Authenticate as Admin
            self.client.force_authenticate(user=self.admin_user)
            approve_url = reverse('admin-approve-lawyer', kwargs={'lawyer_id': profile.user.id})

            response = self.client.post(approve_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['verification_status'], VerificationStatus.APPROVED)
            self.assertTrue(response.data['is_verified'])
            self.assertIsNotNone(response.data['badge'])
            self.assertTrue(response.data['badge']['is_active'])
            self.assertEqual(response.data['badge']['sanad_number'], 'DH-9921')

            # Verify in DB
            profile.refresh_from_db()
            self.assertEqual(profile.verification_status, VerificationStatus.APPROVED)
            self.assertTrue(profile.is_verified)
            self.assertEqual(profile.verified_by, self.admin_user)
            self.assertIsNotNone(profile.verified_at)

    def test_admin_reject_lawyer_requires_reason(self):
        """Admin rejecting lawyer requires a rejection reason; badge remains disabled."""
        lawyer_user = User.objects.create_user(
            email='rejected.lawyer@bar.bd',
            full_name='Adv. Invalid Doc',
            password='Password123',
            role='lawyer'
        )
        profile = LawyerProfile.objects.create(
            user=lawyer_user,
            bar_council_no='DH-0001',
            verification_status=VerificationStatus.PENDING
        )

        self.client.force_authenticate(user=self.admin_user)
        reject_url = reverse('admin-reject-lawyer', kwargs={'lawyer_id': profile.user.id})

        # Failure without reason
        res_fail = self.client.post(reject_url, {})
        self.assertEqual(res_fail.status_code, status.HTTP_400_BAD_REQUEST)

        # Success with reason
        res_success = self.client.post(reject_url, {'rejection_reason': 'NID image is unreadable and Bar Council ID does not match records.'})
        self.assertEqual(res_success.status_code, status.HTTP_200_OK)
        self.assertEqual(res_success.data['verification_status'], VerificationStatus.REJECTED)
        self.assertFalse(res_success.data['is_verified'])
        self.assertIsNone(res_success.data['badge'])

        profile.refresh_from_db()
        self.assertEqual(profile.verification_status, VerificationStatus.REJECTED)
        self.assertIn('NID image is unreadable', profile.rejection_reason)
