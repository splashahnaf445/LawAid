"""
API tests for FR-1 (client + lawyer registration). They run against a real PostgreSQL 18
test database built from db/schema.sql (see config/test_runner.py):

    cd backend && python manage.py test accounts lawyers
"""
from decimal import Decimal

from django.core.cache import cache
from django.db import connection
from django.urls import reverse
from rest_framework import serializers
from rest_framework.test import APITestCase

from accounts.models import ClientProfile, LawyerProfile, User
from accounts.serializers import ClientRegisterSerializer, LawyerRegisterSerializer
from lawyers.models import Court, PracticeArea

PASSWORD = "LawAid@123"


def client_payload(**overrides):
    payload = {
        "full_name": "Ahnaf Shahriar",
        "email": "ahnaf@example.com",
        "phone": "+880 1713-000021",
        "password": PASSWORD,
        "password_confirm": PASSWORD,
        "accept_terms": True,
    }
    payload.update(overrides)
    return payload


class RegistrationTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.court = Court.objects.create(name="Test High Court", court_type="supreme_court", district="Dhaka")
        cls.area1 = PracticeArea.objects.create(slug="t-const", name_en="Constitutional", name_bn="সাংবিধানিক")
        cls.area2 = PracticeArea.objects.create(slug="t-corp", name_en="Corporate", name_bn="কর্পোরেট")

    def setUp(self):
        cache.clear()  # reset the registration throttle between tests

    def lawyer_payload(self, **overrides):
        payload = {
            "full_name": "Adv. Tanvir Ahmed",
            "email": "tanvir@example.com",
            "phone": "+880 1712-345678",
            "primary_court": self.court.pk,
            "bar_council_no": "bc-2018-9412",
            "bar_association": "Supreme Court Bar Association (SCBA)",
            "practice_areas": [self.area1.pk, self.area2.pk],
            "chamber_address": "Chambers 405, Supreme Court Bar",
            "password": PASSWORD,
            "password_confirm": PASSWORD,
            "consultation_fee": 5000,
            "two_factor_enabled": True,
            "accept_terms": True,
        }
        payload.update(overrides)
        return payload

    def post_client(self, **overrides):
        return self.client.post(reverse("register-client"), client_payload(**overrides), format="json")

    def post_lawyer(self, **overrides):
        return self.client.post(reverse("register-lawyer"), self.lawyer_payload(**overrides), format="json")


class ClientRegistrationTests(RegistrationTestCase):
    def test_client_can_register(self):
        res = self.post_client()
        self.assertEqual(res.status_code, 201, res.content)
        self.assertEqual(res.data["role"], "client")
        self.assertEqual(res.data["status"], "active")
        self.assertEqual(res.data["phone"], "+8801713000021")
        self.assertNotIn("password", res.data)
        self.assertNotIn("password_confirm", res.data)

        user = User.objects.get(email="ahnaf@example.com")
        self.assertEqual(user.role, "client")  # role stored
        self.assertTrue(user.check_password(PASSWORD))
        self.assertNotIn(PASSWORD, user.password)  # stored hashed
        self.assertTrue(ClientProfile.objects.filter(user=user).exists())

    def test_phone_is_optional_for_clients(self):
        payload = client_payload()
        del payload["phone"]
        res = self.client.post(reverse("register-client"), payload, format="json")
        self.assertEqual(res.status_code, 201, res.content)
        self.assertIsNone(res.data["phone"])

    def test_role_and_status_in_body_are_ignored(self):
        res = self.post_client(role="admin", status="suspended", is_staff=True)
        self.assertEqual(res.status_code, 201)
        user = User.objects.get(email="ahnaf@example.com")
        self.assertEqual((user.role, user.status), ("client", "active"))

    def test_duplicate_email_is_rejected_case_insensitively(self):
        self.assertEqual(self.post_client().status_code, 201)
        res = self.post_client(email="AHNAF@Example.COM", phone="+8801713000099")
        self.assertEqual(res.status_code, 400)
        self.assertIn("email", res.data)
        self.assertEqual(User.objects.count(), 1)

    def test_duplicate_phone_is_rejected_in_any_format(self):
        self.assertEqual(self.post_client().status_code, 201)
        res = self.post_client(email="other@example.com", phone="01713000021")
        self.assertEqual(res.status_code, 400)
        self.assertIn("phone", res.data)

    def test_field_validation(self):
        cases = [
            ("weak password", {"password": "password", "password_confirm": "password"}, "password"),
            ("short password", {"password": "Ab1!", "password_confirm": "Ab1!"}, "password"),
            ("mismatch", {"password_confirm": "LawAid@124"}, "password_confirm"),
            ("bad phone", {"phone": "12345"}, "phone"),
            ("terms not accepted", {"accept_terms": False}, "accept_terms"),
            ("bad email", {"email": "not-an-email"}, "email"),
            ("blank name", {"full_name": "  "}, "full_name"),
            ("bad language", {"preferred_language": "fr"}, "preferred_language"),
        ]
        for label, overrides, field in cases:
            with self.subTest(label):
                res = self.post_client(**overrides)
                self.assertEqual(res.status_code, 400, res.content)
                self.assertIn(field, res.data)
        self.assertEqual(User.objects.count(), 0)

    def test_missing_required_fields(self):
        res = self.client.post(reverse("register-client"), {}, format="json")
        self.assertEqual(res.status_code, 400)
        for field in ["full_name", "email", "password", "password_confirm", "accept_terms"]:
            self.assertIn(field, res.data)

    def test_password_similar_to_email_is_rejected(self):
        res = self.post_client(email="lawaidfan@example.com", password="Lawaidfan@1", password_confirm="Lawaidfan@1")
        self.assertEqual(res.status_code, 400)
        self.assertIn("password", res.data)

    def test_lost_uniqueness_race_becomes_a_field_error(self):
        """The up-front duplicate check passed, but the row appeared before our INSERT."""
        User.objects.create_user(email="race@example.com", password="x", role="client", full_name="Early Bird")
        with self.assertRaises(serializers.ValidationError) as ctx:
            ClientRegisterSerializer().create(
                {"email": "race@example.com", "password": PASSWORD, "full_name": "Late Comer",
                 "preferred_language": "bn", "phone": None}
            )
        self.assertIn("email", ctx.exception.detail)


class LawyerRegistrationTests(RegistrationTestCase):
    def test_lawyer_can_register_and_is_pending_verification(self):
        res = self.post_lawyer()
        self.assertEqual(res.status_code, 201, res.content)
        self.assertEqual(res.data["role"], "lawyer")
        self.assertEqual(res.data["status"], "pending_verification")
        self.assertEqual(res.data["verification_status"], "pending")
        self.assertEqual(res.data["bar_council_no"], "BC-2018-9412")
        self.assertNotIn("password", res.data)

        user = User.objects.get(email="tanvir@example.com")
        self.assertEqual(user.role, "lawyer")  # role stored
        self.assertEqual(user.full_name, "Tanvir Ahmed")  # honorific split out
        self.assertTrue(user.two_factor_enabled)
        self.assertTrue(user.check_password(PASSWORD))

        profile = LawyerProfile.objects.get(user=user)
        self.assertEqual(profile.honorific, "Adv.")
        self.assertEqual(profile.bar_council_no, "BC-2018-9412")
        self.assertEqual(profile.primary_court_id, self.court.pk)
        self.assertEqual(profile.district, "Dhaka")  # taken from the court
        self.assertEqual(profile.consultation_fee, Decimal("5000.00"))
        self.assertEqual(profile.verification_status, "pending")

        with connection.cursor() as cursor:
            cursor.execute("SELECT practice_area_id FROM lawyer_practice_areas WHERE lawyer_id = %s", [user.pk])
            self.assertCountEqual([r[0] for r in cursor.fetchall()], [self.area1.pk, self.area2.pk])

    def test_fee_is_optional_and_duplicate_areas_are_collapsed(self):
        payload = self.lawyer_payload(practice_areas=[self.area1.pk, self.area1.pk])
        del payload["consultation_fee"]
        res = self.client.post(reverse("register-lawyer"), payload, format="json")
        self.assertEqual(res.status_code, 201, res.content)
        user = User.objects.get(email="tanvir@example.com")
        self.assertEqual(LawyerProfile.objects.get(user=user).consultation_fee, Decimal("0.00"))

    def test_role_in_body_is_ignored(self):
        self.assertEqual(self.post_lawyer(role="admin").status_code, 201)
        self.assertEqual(User.objects.get(email="tanvir@example.com").role, "lawyer")

    def test_email_already_used_by_a_client_is_rejected(self):
        self.assertEqual(self.post_client(email="tanvir@example.com").status_code, 201)
        res = self.post_lawyer()
        self.assertEqual(res.status_code, 400)
        self.assertIn("email", res.data)

    def test_duplicate_bar_council_number_is_rejected(self):
        self.assertEqual(self.post_lawyer().status_code, 201)
        res = self.post_lawyer(email="second@example.com", phone="+8801712999999", bar_council_no="BC-2018-9412")
        self.assertEqual(res.status_code, 400)
        self.assertIn("bar_council_no", res.data)

    def test_field_validation(self):
        cases = [
            ("phone required", {"phone": ""}, "phone"),
            ("unknown court", {"primary_court": 999999}, "primary_court"),
            ("no practice areas", {"practice_areas": []}, "practice_areas"),
            ("unknown practice area", {"practice_areas": [999999]}, "practice_areas"),
            ("bad bar number", {"bar_council_no": "XYZ"}, "bar_council_no"),
            ("negative fee", {"consultation_fee": -1}, "consultation_fee"),
            ("weak password", {"password": "AdvocatePass", "password_confirm": "AdvocatePass"}, "password"),
            ("mismatch", {"password_confirm": "Different@123"}, "password_confirm"),
            ("terms not accepted", {"accept_terms": False}, "accept_terms"),
            ("honorific only", {"full_name": "Adv. X"}, "full_name"),
            ("address required", {"chamber_address": ""}, "chamber_address"),
        ]
        for label, overrides, field in cases:
            with self.subTest(label):
                res = self.post_lawyer(**overrides)
                self.assertEqual(res.status_code, 400, res.content)
                self.assertIn(field, res.data)
        self.assertEqual(User.objects.count(), 0)

    def test_registration_is_all_or_nothing(self):
        """A bar-number clash caught at INSERT time must not leave an orphan users row."""
        self.assertEqual(self.post_lawyer().status_code, 201)
        second = LawyerRegisterSerializer(
            data=self.lawyer_payload(email="second@example.com", phone="+8801712999999", bar_council_no="SC-7841")
        )
        self.assertTrue(second.is_valid(), second.errors)
        vd = dict(second.validated_data, bar_council_no="BC-2018-9412")  # collide after validation
        with self.assertRaises(serializers.ValidationError) as ctx:
            second.create(vd)
        self.assertIn("bar_council_no", ctx.exception.detail)
        self.assertFalse(User.objects.filter(email="second@example.com").exists())


class ReferenceDataTests(RegistrationTestCase):
    def test_courts_and_practice_areas_are_public(self):
        courts = self.client.get(reverse("reference-courts"))
        self.assertEqual(courts.status_code, 200)
        self.assertIn(self.court.pk, [c["id"] for c in courts.json()])

        areas = self.client.get(reverse("reference-practice-areas"))
        self.assertEqual(areas.status_code, 200)
        self.assertEqual([a["slug"] for a in areas.json()], ["t-const", "t-corp"])
