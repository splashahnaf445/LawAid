import os
import shutil
import tempfile
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import User, UserRole
from lawyers.models import LawyerProfile, LawyerVerificationDocument
from core.encryption import DocumentEncryptionService

class DocumentEncryptionAndAccessControlTestCase(TestCase):
    """
    SRS NFR-4 Compliance:
    - 'The system shall never expose a client's or lawyer's uploaded identification documents 
       (NID, Bar Council certificate) to any party other than platform administrators during verification.'
    """
    def setUp(self):
        self.client = APIClient()
        self.temp_storage_dir = tempfile.mkdtemp()

        # Admin
        self.admin = User.objects.create_superuser(
            email='admin@lawaid.gov.bd',
            full_name='Admin Rahid',
            password='AdminPassword123'
        )

        # Client
        self.general_client = User.objects.create_user(
            email='client@lawaid.bd',
            full_name='Client Nafseen',
            password='Password123',
            role=UserRole.CLIENT
        )

        # Other lawyer
        self.other_lawyer = User.objects.create_user(
            email='other@lawaid.bd',
            full_name='Adv. Other',
            password='Password123',
            role=UserRole.LAWYER
        )

        # Target lawyer
        self.target_lawyer = User.objects.create_user(
            email='target@lawaid.bd',
            full_name='Adv. Rezwana',
            password='Password123',
            role=UserRole.LAWYER
        )
        self.target_profile = LawyerProfile.objects.create(
            user=self.target_lawyer,
            bar_council_no='SC-5520'
        )

        # Encrypt document
        raw_nid = b"%PDF-1.4 National Identity Document for Bangladesh Advocate"
        uploaded = SimpleUploadedFile("nid.pdf", raw_nid, "application/pdf")

        with override_settings(ENCRYPTED_DOCUMENTS_DIR=self.temp_storage_dir):
            saved = DocumentEncryptionService.save_encrypted_file(
                uploaded,
                lawyer_id=str(self.target_lawyer.id),
                doc_type="nid"
            )
            self.doc = LawyerVerificationDocument.objects.create(
                lawyer=self.target_profile,
                doc_type='nid',
                file_url=saved['file_path'],
                original_filename=saved['original_filename'],
                mime_type='application/pdf',
                file_size_bytes=saved['file_size_bytes']
            )

    def tearDown(self):
        shutil.rmtree(self.temp_storage_dir, ignore_errors=True)

    def test_document_is_encrypted_on_disk(self):
        """Verifies disk content is unreadable ciphertext."""
        with open(self.doc.file_url, 'rb') as f:
            disk_bytes = f.read()
        self.assertNotIn(b"%PDF-1.4", disk_bytes)
        self.assertNotIn(b"National Identity", disk_bytes)

    def test_anonymous_access_denied(self):
        """NFR-4: Anonymous access strictly denied."""
        url = reverse('admin-view-document', kwargs={'document_id': self.doc.id})
        res = self.client.get(url)
        self.assertIn(res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_client_access_denied(self):
        """NFR-4: Client users strictly denied access (403 Forbidden)."""
        self.client.force_authenticate(user=self.general_client)
        url = reverse('admin-view-document', kwargs={'document_id': self.doc.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_lawyer_access_denied(self):
        """NFR-4: Other lawyers strictly denied access (403 Forbidden)."""
        self.client.force_authenticate(user=self.other_lawyer)
        url = reverse('admin-view-document', kwargs={'document_id': self.doc.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_access_granted_with_decrypted_content(self):
        """NFR-4: Platform admin can view decrypted document stream."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('admin-view-document', kwargs={'document_id': self.doc.id})

        with override_settings(ENCRYPTED_DOCUMENTS_DIR=self.temp_storage_dir):
            res = self.client.get(url)
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertEqual(res['Content-Type'], 'application/pdf')
            self.assertIn(b"National Identity Document for Bangladesh Advocate", res.content)
