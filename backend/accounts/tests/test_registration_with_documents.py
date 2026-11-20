"""
Ahnaf's registration tests (SYS-21), kept from feature/lawyer-verification-and-badge.

Integration changes (integration/merge-all): moved out of test_registration.py because both
branches had a class named RegistrationTestCase. Request payloads now include the fields
required by Usama's registration rules (SYS-18): password_confirm, accept_terms, a password
with upper/lower/number/special characters, and for lawyers primary_court, practice_areas
and chamber_address. The assertions are unchanged.
"""
import os
import shutil
import tempfile
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import User, UserRole
from lawyers.models import Court, LawyerProfile, LawyerVerificationDocument, PracticeArea, VerificationStatus


class RegistrationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.temp_storage_dir = tempfile.mkdtemp()
        self.court = Court.objects.create(
            name='Supreme Court of Bangladesh - High Court Division', court_type='supreme_court', district='Dhaka'
        )
        self.area = PracticeArea.objects.create(slug='constitutional', name_en='Constitutional / Writ', name_bn='সাংবিধানিক / রিট')

    def tearDown(self):
        shutil.rmtree(self.temp_storage_dir, ignore_errors=True)

    def test_client_registration(self):
        url = reverse('register-client')
        payload = {
            'full_name': 'Ahnaf Shahriar',
            'email': 'ahnaf@example.com',
            'phone': '+8801713000021',
            'password': 'ClientPassword@123',
            'password_confirm': 'ClientPassword@123',
            'accept_terms': True,
            'address': 'Dhanmondi, Dhaka'
        }
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='ahnaf@example.com', role=UserRole.CLIENT).exists())

    def test_lawyer_registration_with_mandatory_encrypted_documents(self):
        """SRS FR-2, NFR-4: Lawyers upload NID & Bar Certificate; files stored encrypted."""
        url = reverse('register-lawyer')

        raw_nid = b"%PDF-1.4 National ID Card for Advocate Rezwana"
        raw_cert = b"\x89PNG\r\n\x1a\nBar Council Sanad SC-7841 Certificate"

        nid_file = SimpleUploadedFile("nid.pdf", raw_nid, content_type="application/pdf")
        cert_file = SimpleUploadedFile("sanad.png", raw_cert, content_type="image/png")

        payload = {
            'full_name': 'Adv. Rezwana Karim',
            'email': 'rezwana.karim@lawaid.com.bd',
            'phone': '+8801712000015',
            'password': 'LawyerPassword@123',
            'password_confirm': 'LawyerPassword@123',
            'accept_terms': True,
            'primary_court': self.court.pk,
            'practice_areas': [self.area.pk],
            'chamber_address': 'Supreme Court Bar Annex Building, Ramna, Dhaka 1000',
            'honorific': 'Adv.',
            'headline': 'Senior Advocate, High Court Division',
            'bar_council_no': 'SC-5520',
            'bar_association': 'Supreme Court Bar Association',
            'district': 'Dhaka',
            'specialization': 'Civil Litigation, Writ Petition',
            'consultation_fee': '1500.00',
            'years_experience': 14,
            'bio': '14+ years experience in the High Court.',
            'nid_document': nid_file,
            'bar_certificate_document': cert_file,
        }

        with override_settings(ENCRYPTED_DOCUMENTS_DIR=self.temp_storage_dir):
            res = self.client.post(url, payload, format='multipart')
            self.assertEqual(res.status_code, status.HTTP_201_CREATED)
            self.assertEqual(res.data['verification_status'], VerificationStatus.PENDING)
            self.assertFalse(res.data['is_verified'])
            self.assertIsNone(res.data['badge'])

            # Verify database records
            profile = LawyerProfile.objects.get(bar_council_no='SC-5520')
            self.assertEqual(profile.verification_status, VerificationStatus.PENDING)
            self.assertFalse(profile.is_verified)
            self.assertIsNone(profile.get_verification_badge())

            # Verify encrypted files on disk (NFR-4)
            docs = profile.verification_documents.all()
            self.assertEqual(docs.count(), 2)

            for doc in docs:
                self.assertEqual(doc.status, VerificationStatus.PENDING)
                self.assertTrue(os.path.exists(doc.file_url) or doc.file_url.startswith('private://'))
