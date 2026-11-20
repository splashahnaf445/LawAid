from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import User, UserRole
from lawyers.models import LawyerProfile, VerificationStatus

class LawyerVerificationAndBadgeTestCase(TestCase):
    """
    SRS FR-3 Compliance:
    - 'Show verification badge on lawyer profile only after admin approval; lawyer hidden from search until verified.'
    """
    def setUp(self):
        self.client = APIClient()

        # Admin user
        self.admin = User.objects.create_superuser(
            email='admin@lawaid.gov.bd',
            full_name='Lead Admin Rahid Karim',
            password='AdminPassword123'
        )

        # 1. Approved Lawyer
        self.u1 = User.objects.create_user(
            email='approved@lawaid.bd',
            full_name='Adv. Rafiqul Islam',
            password='Password123',
            role=UserRole.LAWYER
        )
        self.approved_lawyer = LawyerProfile.objects.create(
            user=self.u1,
            bar_council_no='SC-7841',
            district='Dhaka',
            specialization='Civil Litigation',
            verification_status=VerificationStatus.APPROVED,
            verified_at=timezone.now()
        )

        # 2. Pending Lawyer (Must be hidden from public search)
        self.u2 = User.objects.create_user(
            email='pending@lawaid.bd',
            full_name='Adv. Farhan Chowdhury',
            password='Password123',
            role=UserRole.LAWYER
        )
        self.pending_lawyer = LawyerProfile.objects.create(
            user=self.u2,
            bar_council_no='DH-4412',
            district='Dhaka',
            specialization='Criminal Defense',
            verification_status=VerificationStatus.PENDING
        )

        # 3. Rejected Lawyer (Must be hidden from public search)
        self.u3 = User.objects.create_user(
            email='rejected@lawaid.bd',
            full_name='Adv. Imran Sheikh',
            password='Password123',
            role=UserRole.LAWYER
        )
        self.rejected_lawyer = LawyerProfile.objects.create(
            user=self.u3,
            bar_council_no='SC-0099',
            district='Sylhet',
            specialization='Corporate Law',
            verification_status=VerificationStatus.REJECTED,
            rejection_reason='Invalid Sanad'
        )

    def test_search_hides_unverified_lawyers_and_shows_approved_with_badge(self):
        """FR-3: Only approved lawyers appear in search; carry verification badge."""
        url = reverse('lawyer-search')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data['results']

        self.assertEqual(len(results), 1)
        bar_nos = [r['bar_council_no'] for r in results]
        self.assertIn('SC-7841', bar_nos)
        self.assertNotIn('DH-4412', bar_nos)  # Pending is hidden
        self.assertNotIn('SC-0099', bar_nos)  # Rejected is hidden

        # Check badge
        approved_res = results[0]
        self.assertTrue(approved_res['is_verified'])
        self.assertIsNotNone(approved_res['verification_badge'])
        self.assertTrue(approved_res['verification_badge']['is_active'])
        self.assertEqual(approved_res['verification_badge']['sanad_number'], 'SC-7841')

    def test_admin_approve_lawyer_awards_badge(self):
        """Admin approves lawyer; status becomes 'approved' and badge is enabled."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('admin-approve-lawyer', kwargs={'lawyer_id': self.u2.id})

        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['verification_status'], VerificationStatus.APPROVED)
        self.assertTrue(res.data['is_verified'])
        self.assertIsNotNone(res.data['badge'])

        self.pending_lawyer.refresh_from_db()
        self.assertEqual(self.pending_lawyer.verification_status, VerificationStatus.APPROVED)

    def test_admin_reject_lawyer_requires_reason(self):
        """Admin rejecting lawyer requires a reason."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('admin-reject-lawyer', kwargs={'lawyer_id': self.u2.id})

        # No reason -> 400
        res_fail = self.client.post(url, {})
        self.assertEqual(res_fail.status_code, status.HTTP_400_BAD_REQUEST)

        # With reason -> 200
        res_ok = self.client.post(url, {'rejection_reason': 'NID is expired'})
        self.assertEqual(res_ok.status_code, status.HTTP_200_OK)
        self.assertEqual(res_ok.data['verification_status'], VerificationStatus.REJECTED)
        self.assertFalse(res_ok.data['is_verified'])
        self.assertIsNone(res_ok.data['badge'])
