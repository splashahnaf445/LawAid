import shutil
import tempfile
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import User, LawyerProfile, LawyerVerificationDocument, VerificationStatus
from accounts.encryption import DocumentEncryptionService

class DocumentAccessControlTestCase(TestCase):
    """
    SRS NFR-4 Compliance:
    - 'The system shall never expose a client's or lawyer's uploaded identification documents 
       (NID, Bar Council certificate) to any party other than platform administrators during verification.'
    """
    def setUp(self):
        self.client = APIClient()
        self.temp_storage_dir = tempfile.mkdtemp()

        # 1. Admin User
        self.admin = User.objects.create_superuser(
            email='admin.compliance@lawaid.gov.bd',
            full_name='Platform Admin Rahid',
            password='AdminPassword123'
        )

        # 2. General Client User
        self.general_client = User.objects.create_user(
            email='client.user@gmail.com',
            full_name='Client Nafseen',
            password='Password123',
            role='client'
        )

        # 3. Third-party Lawyer
        self.other_lawyer = User.objects.create_user(
            email='other.lawyer@law.bd',
            full_name='Adv. Competitor',
            password='Password123',
            role='lawyer'
        )

        # 4. Target Lawyer whose documents were uploaded
        self.target_lawyer_user = User.objects.create_user(
            email='target.lawyer@apexlegal.bd',
            full_name='Adv. Syeda Farhana',
            password='Password123',
            role='lawyer'
        )
        self.target_profile = LawyerProfile.objects.create(
            user=self.target_lawyer_user,
            bar_council_no='SC-7841'
        )

        # Create encrypted document
        raw_doc_bytes = b"%PDF-1.4 National Identity Card Confidentially Uploaded"
        uploaded_doc = SimpleUploadedFile("nid_secure.pdf", raw_doc_bytes, "application/pdf")
        
        with override_settings(ENCRYPTED_DOCUMENTS_DIR=self.temp_storage_dir):
            saved = DocumentEncryptionService.save_encrypted_file(
                uploaded_doc, 
                lawyer_id=str(self.target_lawyer_user.id), 
                doc_type="nid"
            )
            self.doc = LawyerVerificationDocument.objects.create(
                lawyer=self.target_profile,
                doc_type='nid',
                file_path=saved['file_path'],
                original_filename=saved['original_filename'],
                mime_type='application/pdf',
                file_size_bytes=saved['file_size_bytes']
            )

    def tearDown(self):
        shutil.rmtree(self.temp_storage_dir, ignore_errors=True)

    def test_anonymous_user_denied_access(self):
        """Anonymous users must receive 401/403 (NFR-4)."""
        url = reverse('admin-view-doc', kwargs={'document_id': self.doc.id})
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_client_user_denied_access(self):
        """General clients attempting to access lawyer documents must receive 403 Forbidden (NFR-4)."""
        self.client.force_authenticate(user=self.general_client)
        url = reverse('admin-view-doc', kwargs={'document_id': self.doc.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_lawyer_denied_access(self):
        """Another lawyer attempting to access verification documents must receive 403 Forbidden (NFR-4)."""
        self.client.force_authenticate(user=self.other_lawyer)
        url = reverse('admin-view-doc', kwargs={'document_id': self.doc.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_granted_access_and_receives_decrypted_stream(self):
        """Platform administrators are authorized to view decrypted document (NFR-4)."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('admin-view-doc', kwargs={'document_id': self.doc.id})
        
        with override_settings(ENCRYPTED_DOCUMENTS_DIR=self.temp_storage_dir):
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response['Content-Type'], 'application/pdf')
            # Verify response content is decrypted plaintext matching original
            self.assertIn(b"National Identity Card Confidentially Uploaded", response.content)
