from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.validators import validate_bd_phone, validate_bar_council_no, validate_verification_document, normalize_bd_phone

class AccountsValidatorsTestCase(TestCase):
    def test_normalize_bd_phone(self):
        self.assertEqual(normalize_bd_phone('01712345678'), '+8801712345678')
        self.assertEqual(normalize_bd_phone('+8801712345678'), '+8801712345678')
        self.assertEqual(normalize_bd_phone('8801712345678'), '+8801712345678')

    def test_validate_bd_phone(self):
        validate_bd_phone('+8801712345678')
        with self.assertRaises(ValidationError):
            validate_bd_phone('01212345678')  # Invalid operator prefix

    def test_validate_bar_council_no(self):
        validate_bar_council_no('SC-7841')
        validate_bar_council_no('DH-10492')
        with self.assertRaises(ValidationError):
            validate_bar_council_no('!')

    def test_validate_verification_document(self):
        valid_pdf = SimpleUploadedFile("cert.pdf", b"%PDF-1.4...", content_type="application/pdf")
        validate_verification_document(valid_pdf)

        invalid_exe = SimpleUploadedFile("danger.exe", b"MZ...", content_type="application/octet-stream")
        with self.assertRaises(ValidationError):
            validate_verification_document(invalid_exe)
