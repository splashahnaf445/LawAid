import os
import shutil
import tempfile
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.encryption import DocumentEncryptionService

class DocumentEncryptionServiceTestCase(TestCase):
    """
    Unit tests for DocumentEncryptionService.
    SRS Compliance:
    - FR-2: Document upload during registration.
    - NFR-1: Sensitive data encrypted at rest.
    - NFR-4: Files stored encrypted and protected.
    """
    def setUp(self):
        self.temp_storage_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_storage_dir, ignore_errors=True)

    def test_encrypt_and_decrypt_bytes(self):
        raw_data = b"CONFIDENTIAL BANGLADESH BAR COUNCIL SANAD CERTIFICATE - ADVOCATE 7841"
        encrypted = DocumentEncryptionService.encrypt_bytes(raw_data)
        
        # Ciphertext must not contain plaintext
        self.assertNotEqual(raw_data, encrypted)
        self.assertNotIn(b"SANAD", encrypted)
        
        # Decrypted ciphertext must exactly match original plaintext
        decrypted = DocumentEncryptionService.decrypt_bytes(encrypted)
        self.assertEqual(raw_data, decrypted)

    def test_save_encrypted_file_stores_ciphertext_on_disk(self):
        raw_content = b"%PDF-1.4 National ID Card for Advocate Rezwana Karim"
        uploaded_file = SimpleUploadedFile(
            name="nid_advocate.pdf",
            content=raw_content,
            content_type="application/pdf"
        )

        with override_settings(ENCRYPTED_DOCUMENTS_DIR=self.temp_storage_dir):
            metadata = DocumentEncryptionService.save_encrypted_file(
                uploaded_file=uploaded_file,
                lawyer_id="test-lawyer-123",
                doc_type="nid"
            )

            # Check metadata
            self.assertTrue(os.path.exists(metadata['file_path']))
            self.assertEqual(metadata['original_filename'], "nid_advocate.pdf")
            self.assertEqual(metadata['mime_type'], "application/pdf")
            self.assertEqual(metadata['file_size_bytes'], len(raw_content))

            # Inspect physical file on disk: verify it is encrypted ciphertext, NOT plaintext
            with open(metadata['file_path'], 'rb') as f:
                disk_content = f.read()

            self.assertNotEqual(disk_content, raw_content)
            self.assertNotIn(b"%PDF-1.4", disk_content)
            self.assertNotIn(b"National ID", disk_content)

            # Read through service: must decrypt perfectly
            decrypted = DocumentEncryptionService.read_and_decrypt_file(metadata['file_path'])
            self.assertEqual(decrypted, raw_content)
