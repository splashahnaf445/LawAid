"""
Tests for password recovery endpoints (SYS-20 / SRS FR-5).
Author: Mashruba Aktar

Coverage
--------
Forgot-password (POST /api/auth/password/forgot/)
  - unknown email → 200 with the standard success message
  - known email   → 200, token created in DB, email sent to console backend
  - unknown phone → 200 with the standard success message
  - known phone   → 200, token created in DB (phone path)
  - both fields   → 400 with non_field_errors
  - neither field → 400 with non_field_errors
  - invalid email format → 400
  - invalid phone format → 400

Reset-password (POST /api/auth/password/reset/)
  - valid token + good password → 200, password changed, user can log in
  - expired token → 400 with token error
  - used (already-consumed) token → 400 with token error
  - wrong/nonexistent token → 400 with token error
  - weak password (too short) → 400 with new_password error
  - numeric-only password → 400 with new_password error
  - after reset, other unused tokens for the same user are invalidated
"""

from datetime import timedelta

from django.contrib.auth import authenticate
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User
from accounts.password_reset import PasswordResetToken, generate_raw_token, hash_token

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

FORGOT_URL = reverse("password-forgot")
RESET_URL  = reverse("password-reset")

_SUCCESS_200 = {
    "status": "success",
    "message": "If an account matches, a password reset link has been sent.",
}
_SUCCESS_RESET_200 = {
    "status": "success",
    "message": "Your password has been reset. Please log in with the new password.",
}

# Use in-memory email backend so we can inspect outbox.
EMAIL_OVERRIDES = {
    "EMAIL_BACKEND": "django.core.mail.backends.locmem.EmailBackend",
}


def _make_user(email="ayesha@test.com", phone="+8801711111111", password="ValidPass@1"):
    return User.objects.create_user(
        email=email,
        full_name="Ayesha Test",
        password=password,
        role="client",
        phone=phone,
    )


# ===========================================================================
# Forgot-password tests
# ===========================================================================


@override_settings(**EMAIL_OVERRIDES)
class ForgotPasswordViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = _make_user()

    # --- Email path ---------------------------------------------------------

    def test_unknown_email_returns_200(self):
        resp = self.client.post(FORGOT_URL, {"email": "nobody@example.com"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), _SUCCESS_200)

    def test_known_email_returns_200_creates_token_sends_email(self):
        resp = self.client.post(FORGOT_URL, {"email": self.user.email}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), _SUCCESS_200)

        # Token must exist in DB
        tokens = PasswordResetToken.objects.filter(user=self.user)
        self.assertEqual(tokens.count(), 1)
        self.assertTrue(tokens.first().is_valid)

        # Email must have been dispatched
        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertIn(self.user.email, sent.to)
        self.assertIn("reset-password", sent.body)

    def test_invalid_email_format_returns_400(self):
        resp = self.client.post(FORGOT_URL, {"email": "not-an-email"}, format="json")
        self.assertEqual(resp.status_code, 400)

    # --- Phone path ---------------------------------------------------------

    def test_unknown_phone_returns_200(self):
        resp = self.client.post(FORGOT_URL, {"phone": "+8801799999999"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), _SUCCESS_200)

    def test_known_phone_returns_200_creates_token(self):
        resp = self.client.post(FORGOT_URL, {"phone": self.user.phone}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), _SUCCESS_200)

        tokens = PasswordResetToken.objects.filter(user=self.user)
        self.assertEqual(tokens.count(), 1)
        self.assertTrue(tokens.first().is_valid)

    def test_invalid_phone_format_returns_400(self):
        # A string that is not a valid BD phone number
        resp = self.client.post(FORGOT_URL, {"phone": "12345"}, format="json")
        self.assertEqual(resp.status_code, 400)

    # --- Validation of field presence --------------------------------------

    def test_both_email_and_phone_returns_400(self):
        resp = self.client.post(
            FORGOT_URL,
            {"email": self.user.email, "phone": self.user.phone},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)
        body = resp.json()
        # API contract: non_field_errors key
        self.assertIn("non_field_errors", body)
        self.assertIn("Provide either email or phone.", body["non_field_errors"])

    def test_neither_email_nor_phone_returns_400(self):
        resp = self.client.post(FORGOT_URL, {}, format="json")
        self.assertEqual(resp.status_code, 400)
        body = resp.json()
        self.assertIn("non_field_errors", body)
        self.assertIn("Provide either email or phone.", body["non_field_errors"])

    def test_blank_strings_treated_as_absent(self):
        resp = self.client.post(
            FORGOT_URL, {"email": "", "phone": ""}, format="json"
        )
        self.assertEqual(resp.status_code, 400)
        body = resp.json()
        self.assertIn("non_field_errors", body)


# ===========================================================================
# Reset-password tests
# ===========================================================================


@override_settings(**EMAIL_OVERRIDES)
class ResetPasswordViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = _make_user(password="OldPassword@1")

    def _make_token(self):
        _, raw = PasswordResetToken.create_for_user(self.user)
        return raw

    # --- Happy path ---------------------------------------------------------

    def test_valid_token_resets_password_and_user_can_login(self):
        raw = self._make_token()
        resp = self.client.post(
            RESET_URL,
            {"token": raw, "new_password": "NewLawAid@456"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), _SUCCESS_RESET_200)

        # Token must now be marked used
        obj = PasswordResetToken.objects.get(token_hash=hash_token(raw))
        self.assertTrue(obj.is_used)

        # User must be able to authenticate with the new password
        user = authenticate(username=self.user.email, password="NewLawAid@456")
        self.assertIsNotNone(user)

    def test_valid_reset_invalidates_other_unused_tokens(self):
        # Create two tokens; use the first to reset; the second must be invalidated.
        raw1 = self._make_token()
        raw2 = self._make_token()

        self.client.post(
            RESET_URL,
            {"token": raw1, "new_password": "NewLawAid@456"},
            format="json",
        )

        obj2 = PasswordResetToken.objects.get(token_hash=hash_token(raw2))
        self.assertTrue(obj2.is_used, "Second token should have been invalidated")

    # --- Token rejection cases ----------------------------------------------

    def test_expired_token_returns_400(self):
        raw = self._make_token()
        # Force expiry
        PasswordResetToken.objects.filter(token_hash=hash_token(raw)).update(
            expires_at=timezone.now() - timedelta(minutes=1)
        )
        resp = self.client.post(
            RESET_URL, {"token": raw, "new_password": "NewLawAid@456"}, format="json"
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("token", resp.json())
        self.assertIn("invalid or has expired", resp.json()["token"][0])

    def test_used_token_returns_400(self):
        raw = self._make_token()
        # Consume it manually
        obj = PasswordResetToken.objects.get(token_hash=hash_token(raw))
        obj.consume()

        resp = self.client.post(
            RESET_URL, {"token": raw, "new_password": "NewLawAid@456"}, format="json"
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("token", resp.json())

    def test_wrong_token_returns_400(self):
        resp = self.client.post(
            RESET_URL,
            {"token": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
             "new_password": "NewLawAid@456"},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("token", resp.json())

    # --- Password validation cases -----------------------------------------

    def test_too_short_password_returns_400(self):
        raw = self._make_token()
        resp = self.client.post(
            RESET_URL, {"token": raw, "new_password": "abc"}, format="json"
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("new_password", resp.json())

    def test_numeric_only_password_returns_400(self):
        raw = self._make_token()
        resp = self.client.post(
            RESET_URL, {"token": raw, "new_password": "123456789"}, format="json"
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("new_password", resp.json())

    def test_common_password_returns_400(self):
        raw = self._make_token()
        resp = self.client.post(
            RESET_URL, {"token": raw, "new_password": "password"}, format="json"
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("new_password", resp.json())
