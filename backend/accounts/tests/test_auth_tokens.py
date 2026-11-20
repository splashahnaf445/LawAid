from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import User, UserRole, AccountStatus
from lawyers.models import LawyerProfile, VerificationStatus

class AuthTokenPayloadTests(APITestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.admin = User.objects.create_user(
            email="admin@test.com",
            password=self.password,
            full_name="Admin Officer",
            role=UserRole.ADMIN,
            status=AccountStatus.ACTIVE
        )
        self.verified_lawyer_user = User.objects.create_user(
            email="verified@test.com",
            password=self.password,
            full_name="Advocate Test",
            role=UserRole.LAWYER,
            status=AccountStatus.ACTIVE
        )
        self.verified_lawyer = LawyerProfile.objects.create(
            user=self.verified_lawyer_user,
            bar_council_no="77889/2015",
            verification_status=VerificationStatus.APPROVED
        )

    def test_login_returns_token_and_user_verification_payload(self):
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {
            'email': self.verified_lawyer_user.email,
            'password': self.password
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        
        user_data = response.data['user']
        self.assertEqual(user_data['email'], self.verified_lawyer_user.email)
        self.assertEqual(user_data['role'], 'lawyer')
        self.assertEqual(user_data['verification_status'], 'approved')
        self.assertTrue(user_data['is_verified'])
        self.assertEqual(user_data['bar_council_no'], '77889/2015')
        self.assertIsNotNone(user_data['badge'])
        self.assertEqual(user_data['badge']['sanad_number'], '77889/2015')

    def test_current_user_me_endpoint_requires_auth(self):
        url = reverse('current-user')
        # Unauthenticated
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Authenticated
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.admin.email)
        self.assertTrue(response.data['is_admin'])
