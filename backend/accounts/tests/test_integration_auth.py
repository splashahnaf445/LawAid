"""
Integration tests added on integration/merge-all for the parts that had to be joined:
Saker's cookie-based login (SYS-19, main flow), Ahnaf's SimpleJWT tokens (kept for the API
contract) and Usama's registration statuses (SYS-18).
"""
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase

from accounts.models import AccountStatus, RefreshToken, User, UserRole
from lawyers.models import LawyerProfile, VerificationStatus

PASSWORD = "LawAid@123"
XHR = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}


class CookieLoginIntegrationTests(APITestCase):
    def setUp(self):
        cache.clear()  # reset the login throttle
        self.lawyer = User.objects.create_user(
            email="farhan.chowdhury@example.com", full_name="Farhan Chowdhury", password=PASSWORD,
            role=UserRole.LAWYER, status=AccountStatus.PENDING_VERIFICATION,
        )
        LawyerProfile.objects.create(user=self.lawyer, bar_council_no="DH-22871",
                                     verification_status=VerificationStatus.PENDING)

    def login(self, email="farhan.chowdhury@example.com", password=PASSWORD, **extra):
        return self.client.post(reverse("auth-login"), {"email": email, "password": password, **extra}, format="json")

    def test_pending_lawyer_can_log_in_and_sees_verification_status(self):
        res = self.login(email="Farhan.Chowdhury@Example.com")  # email is case-insensitive
        self.assertEqual(res.status_code, 200, res.content)
        self.assertIn("access", res.data)
        self.assertIn("lawaid_refresh", res.cookies)
        self.assertTrue(res.cookies["lawaid_refresh"]["httponly"])
        self.assertEqual(res.data["user"]["role"], "lawyer")
        self.assertEqual(res.data["user"]["verification_status"], "pending")
        self.assertEqual(RefreshToken.objects.filter(user=self.lawyer).count(), 1)

    def test_suspended_account_cannot_log_in(self):
        User.objects.filter(pk=self.lawyer.pk).update(status=AccountStatus.SUSPENDED)
        res = self.login()
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.data["code"], "account_suspended")

    def test_wrong_portal_is_rejected(self):
        res = self.login(portal="client")
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.data["code"], "wrong_portal")

    def test_me_accepts_both_token_types(self):
        cookie_access = self.login().data["access"]
        res = self.client.get(reverse("current-user"), HTTP_AUTHORIZATION=f"Bearer {cookie_access}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["bar_council_no"], "DH-22871")

        simplejwt = self.client.post(
            reverse("token_obtain_pair"), {"email": self.lawyer.email, "password": PASSWORD}, format="json"
        )
        self.assertEqual(simplejwt.status_code, 200, simplejwt.content)
        res = self.client.get(reverse("current-user"), HTTP_AUTHORIZATION=f"Bearer {simplejwt.data['access']}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["email"], self.lawyer.email)

        res = self.client.get(reverse("current-user"), HTTP_AUTHORIZATION="Bearer not-a-token")
        self.assertEqual(res.status_code, 401)

    def test_refresh_rotates_cookie_and_requires_xhr_header(self):
        self.login()
        self.assertEqual(self.client.post(reverse("auth-refresh")).status_code, 403)  # CSRF guard

        res = self.client.post(reverse("auth-refresh"), **XHR)
        self.assertEqual(res.status_code, 200, res.content)
        self.assertIn("access", res.data)
        self.assertEqual(RefreshToken.objects.filter(user=self.lawyer, revoked_at__isnull=True).count(), 1)
        self.assertEqual(RefreshToken.objects.filter(user=self.lawyer, revoked_at__isnull=False).count(), 1)

    def test_logout_revokes_refresh_token(self):
        self.login()
        res = self.client.post(reverse("auth-logout"), **XHR)
        self.assertEqual(res.status_code, 204)
        self.assertFalse(RefreshToken.objects.filter(user=self.lawyer, revoked_at__isnull=True).exists())

    def test_approval_activates_pending_lawyer(self):
        admin = User.objects.create_user(email="admin@example.com", full_name="Rahid Karim", password=PASSWORD,
                                         role=UserRole.ADMIN, status=AccountStatus.ACTIVE)
        self.client.force_authenticate(user=admin)
        res = self.client.post(reverse("admin-approve-lawyer", args=[self.lawyer.pk]))
        self.assertEqual(res.status_code, 200, res.content)
        self.lawyer.refresh_from_db()
        self.assertEqual(self.lawyer.status, AccountStatus.ACTIVE)
