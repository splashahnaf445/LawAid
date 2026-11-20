"""Pure-function tests: no database needed."""
import unittest
import uuid

from accounts import validators as v
from core.ids import uuid7


class PhoneTests(unittest.TestCase):
    def test_accepted_formats_normalise_to_e164(self):
        for raw in ["+8801712345678", "+880 1712-345678", "8801712345678", "01712345678", "01712 345 678"]:
            with self.subTest(raw=raw):
                self.assertEqual(v.normalize_bd_phone(raw), "+8801712345678")

    def test_rejected(self):
        for raw in ["", "12345", "+8801212345678", "+88017123456", "+8801712345678x", "+44 7712 345678", "1712345678"]:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    v.normalize_bd_phone(raw)

    def test_matches_db_check_constraint(self):
        import re
        db_check = re.compile(r"^\+8801[3-9][0-9]{8}$")
        for raw in ["01312345678", "01912345678", "+880 1512-345678"]:
            self.assertRegex(v.normalize_bd_phone(raw), db_check)


class BarCouncilTests(unittest.TestCase):
    def test_project_formats_accepted(self):
        for raw, expected in [("SC-7841", "SC-7841"), ("dh-10492", "DH-10492"),
                              (" BC-2018-9412 ", "BC-2018-9412"), ("sc - 7841", "SC-7841")]:
            with self.subTest(raw=raw):
                self.assertEqual(v.normalize_bar_council_no(raw), expected)

    def test_rejected(self):
        for raw in ["", "7841", "S-7841", "SC7841", "SC-78", "SC-1234567", "SC-7841; DROP TABLE"]:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    v.normalize_bar_council_no(raw)


class NameTests(unittest.TestCase):
    def test_split_honorific(self):
        cases = {
            "Adv. Tanvir Ahmed": ("Adv.", "Tanvir Ahmed"),
            "adv Tanvir Ahmed": ("Adv.", "Tanvir Ahmed"),
            "Advocate Nusrat Adil": ("Adv.", "Nusrat Adil"),
            "Barrister Tariq Rahman": ("Barrister", "Tariq Rahman"),
            "Barr. Tariq Rahman": ("Barrister", "Tariq Rahman"),
            "Rafiqul Islam": (None, "Rafiqul Islam"),
            "Advani Kumar": (None, "Advani Kumar"),        # not an honorific
            "Barrington Lee": (None, "Barrington Lee"),
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(v.split_honorific(raw), expected)

    def test_clean_full_name(self):
        self.assertEqual(v.clean_full_name("  Ayesha   Rahman "), "Ayesha Rahman")
        self.assertEqual(v.clean_full_name("আয়েশা রহমান"), "আয়েশা রহমান")   # Bangla names are fine
        for bad in ["", " ", "A", "1234", "!!"]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    v.clean_full_name(bad)


class PasswordTests(unittest.TestCase):
    def test_strong_passwords_have_no_problems(self):
        for pw in ["LawAid@123", "AdvocateSupreme#2024"]:
            self.assertEqual(v.password_problems(pw), [])

    def test_each_missing_class_is_reported(self):
        self.assertEqual(len(v.password_problems("password")), 3)   # upper, number, special
        self.assertEqual(len(v.password_problems("PASSWORD1!")), 1)  # lowercase
        self.assertEqual(len(v.password_problems("lawaid@123")), 1)  # uppercase
        self.assertEqual(len(v.password_problems("LawAid@abc")), 1)  # number
        self.assertEqual(len(v.password_problems("LawAid1234")), 1)  # special


class Uuid7Tests(unittest.TestCase):
    def test_version_variant_and_ordering(self):
        a = uuid7()
        self.assertEqual(a.version, 7)
        self.assertEqual(a.variant, uuid.RFC_4122)
        import time
        time.sleep(0.005)
        b = uuid7()
        self.assertLess(a.int >> 80, (b.int >> 80) + 1)  # timestamp prefix is non-decreasing
        self.assertNotEqual(a, b)


if __name__ == "__main__":
    unittest.main()
