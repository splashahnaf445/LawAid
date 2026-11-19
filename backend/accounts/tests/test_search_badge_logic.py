from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone

from accounts.models import User, LawyerProfile, VerificationStatus

class LawyerSearchAndBadgeLogicTestCase(TestCase):
    """
    SRS FR-3 Compliance:
    - 'Show verification badge on lawyer profile only after admin approval; lawyer hidden from search until verified.'
    """
    def setUp(self):
        self.client = APIClient()

        # 1. Approved Lawyer (Should be visible in search with badge)
        self.u1 = User.objects.create_user(
            email='approved.lawyer@bar.bd',
            full_name='Adv. Syeda Farhana',
            password='Password123',
            role='lawyer'
        )
        self.approved_lawyer = LawyerProfile.objects.create(
            user=self.u1,
            bar_council_no='SC-1001',
            district='Dhaka',
            specialization='Writ Petition & Civil',
            verification_status=VerificationStatus.APPROVED,
            verified_at=timezone.now()
        )

        # 2. Pending Lawyer (Must be HIDDEN from search; no badge)
        self.u2 = User.objects.create_user(
            email='pending.lawyer@bar.bd',
            full_name='Adv. Kazi Tanvir',
            password='Password123',
            role='lawyer'
        )
        self.pending_lawyer = LawyerProfile.objects.create(
            user=self.u2,
            bar_council_no='DH-2002',
            district='Dhaka',
            specialization='Criminal Law',
            verification_status=VerificationStatus.PENDING
        )

        # 3. Rejected Lawyer (Must be HIDDEN from search; no badge)
        self.u3 = User.objects.create_user(
            email='rejected.lawyer@bar.bd',
            full_name='Adv. Tamim Iqbal',
            password='Password123',
            role='lawyer'
        )
        self.rejected_lawyer = LawyerProfile.objects.create(
            user=self.u3,
            bar_council_no='CH-3003',
            district='Chittagong',
            specialization='Corporate Law',
            verification_status=VerificationStatus.REJECTED,
            rejection_reason='Invalid credentials'
        )

    def test_search_shows_only_approved_lawyers_and_hides_unverified(self):
        """Unverified lawyers (pending and rejected) are hidden from search (FR-3)."""
        url = reverse('lawyer-search')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']

        # Only approved lawyer must be present
        self.assertEqual(len(results), 1)
        returned_bar_nos = [r['bar_council_no'] for r in results]
        self.assertIn('SC-1001', returned_bar_nos)
        self.assertNotIn('DH-2002', returned_bar_nos)  # Pending is hidden
        self.assertNotIn('CH-3003', returned_bar_nos)  # Rejected is hidden

        # Approved lawyer in search result must include active verification badge
        approved_result = results[0]
        self.assertTrue(approved_result['is_verified'])
        self.assertEqual(approved_result['verification_status'], 'approved')
        self.assertIsNotNone(approved_result['verification_badge'])
        self.assertTrue(approved_result['verification_badge']['is_active'])
        self.assertEqual(approved_result['verification_badge']['title'], 'Bar Council Verified Advocate')

    def test_public_profile_access_rules(self):
        """Approved profile has badge; pending profile is hidden from public."""
        # Approved profile
        url_approved = reverse('lawyer-profile-detail', kwargs={'lawyer_id': self.u1.id})
        res_approved = self.client.get(url_approved)
        self.assertEqual(res_approved.status_code, status.HTTP_200_OK)
        self.assertTrue(res_approved.data['is_verified'])
        self.assertIsNotNone(res_approved.data['verification_badge'])

        # Pending profile accessed anonymously -> 404 Hidden
        url_pending = reverse('lawyer-profile-detail', kwargs={'lawyer_id': self.u2.id})
        res_pending = self.client.get(url_pending)
        self.assertEqual(res_pending.status_code, status.HTTP_404_NOT_FOUND)
