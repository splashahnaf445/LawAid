"""
Validation rules for registration (SYS-18 / FR-1).

The core rules are plain functions with no Django dependency so they are easy to
unit-test and to mirror in the frontend (frontend/src/utils/validators.js).
"""
import re

# ---------------------------------------------------------------------------
# Phone  (DB CHECK: ^\+8801[3-9][0-9]{8}$)
# ---------------------------------------------------------------------------
_PHONE_SEPARATORS = re.compile(r"[\s\-().]")
_BD_MOBILE_TAIL = re.compile(r"1[3-9][0-9]{8}")


def normalize_bd_phone(raw: str) -> str:
    """Accept '+880 1712-345678', '8801712345678', '01712345678' -> '+8801712345678'."""
    s = _PHONE_SEPARATORS.sub("", raw or "")
    if s.startswith("+880"):
        tail = s[4:]
    elif s.startswith("880"):
        tail = s[3:]
    elif s.startswith("0"):
        tail = s[1:]
    else:
        raise ValueError("Enter a valid Bangladesh mobile number, e.g. +8801712345678.")
    if not _BD_MOBILE_TAIL.fullmatch(tail):
        raise ValueError("Enter a valid Bangladesh mobile number, e.g. +8801712345678.")
    return "+880" + tail


# ---------------------------------------------------------------------------
# Bar Council number.  Formats in the project data: SC-7841, DH-10492, BC-2018-9412
# Change BAR_COUNCIL_RE here (and in the frontend validators.js) if the real
# Bar Council format differs.
# ---------------------------------------------------------------------------
BAR_COUNCIL_RE = re.compile(r"[A-Z]{2,5}-(?:[0-9]{4}-)?[0-9]{3,6}")


def normalize_bar_council_no(raw: str) -> str:
    s = re.sub(r"\s*-\s*", "-", (raw or "").strip().upper())
    if not BAR_COUNCIL_RE.fullmatch(s):
        raise ValueError("Enter a valid Bar Council number, e.g. SC-7841 or BC-2018-9412.")
    return s


# ---------------------------------------------------------------------------
# Names. The prototype asks for "Full name (with honorific)"; the DB keeps the
# honorific in lawyer_profiles.honorific and the bare name in users.full_name.
# ---------------------------------------------------------------------------
_HONORIFIC_RE = re.compile(r"^\s*(adv(?:ocate)?|barr(?:ister)?)\.?\s+(\S.*)$", re.IGNORECASE)


def clean_full_name(raw: str) -> str:
    name = re.sub(r"\s+", " ", (raw or "").strip())
    if len(name) < 2 or not any(ch.isalpha() for ch in name):
        raise ValueError("Enter your full name.")
    return name


def split_honorific(full_name: str):
    """'Adv. Tanvir Ahmed' -> ('Adv.', 'Tanvir Ahmed'); no honorific -> (None, name)."""
    m = _HONORIFIC_RE.match(full_name)
    if not m:
        return None, full_name
    honorific = "Adv." if m.group(1).lower().startswith("adv") else "Barrister"
    return honorific, m.group(2).strip()


# ---------------------------------------------------------------------------
# Password
# ---------------------------------------------------------------------------
def password_problems(password: str) -> list:
    """Human-readable list of unmet complexity rules (empty list = OK)."""
    problems = []
    if not re.search(r"[a-z]", password):
        problems.append("Add a lowercase letter.")
    if not re.search(r"[A-Z]", password):
        problems.append("Add an uppercase letter.")
    if not re.search(r"[0-9]", password):
        problems.append("Add a number.")
    if not re.search(r"[^A-Za-z0-9]", password):
        problems.append("Add a special character (e.g. @ # $ !).")
    return problems


class PasswordComplexityValidator:
    """Django AUTH_PASSWORD_VALIDATORS entry. Length is enforced by MinimumLengthValidator."""

    def validate(self, password, user=None):
        from django.core.exceptions import ValidationError

        problems = password_problems(password)
        if problems:
            raise ValidationError(problems, code="password_too_simple")

    def get_help_text(self):
        return "Your password must include upper and lower case letters, a number and a special character."
