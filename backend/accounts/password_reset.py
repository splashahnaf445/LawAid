"""
Password Reset Token model for SYS-20 / SRS FR-5.

Design decisions
----------------
* Only a SHA-256 hash of the raw token is stored in the DB (security).
* The raw 32-byte (64 hex char) token is generated once, sent in the link,
  and never persisted.
* Token lifetime: 30 minutes (PASSWORD_RESET_TOKEN_EXPIRY_MINUTES in settings).
* Single-use: used_at is set on first successful reset.
* invalidate_other_tokens() marks all other unused tokens for the same user
  as used so only one valid link can exist per user at any time.
"""

import hashlib
import os
import binascii
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from .models import User


def _default_expiry():
    minutes = getattr(settings, "PASSWORD_RESET_TOKEN_EXPIRY_MINUTES", 30)
    return timezone.now() + timedelta(minutes=minutes)


def generate_raw_token() -> str:
    """Return a 64-character cryptographically-random hex string."""
    return binascii.hexlify(os.urandom(32)).decode()


def hash_token(raw_token: str) -> str:
    """Return the SHA-256 hex digest of *raw_token*."""
    return hashlib.sha256(raw_token.encode()).hexdigest()


class PasswordResetToken(models.Model):
    """
    Stores a hashed, single-use password-reset token.
    SRS FR-5, SYS-20 (Mashruba Aktar).
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
    )
    # Only the hash is ever written to the DB.
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=_default_expiry)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "lawaid_password_reset_tokens"
        verbose_name = "Password Reset Token"
        verbose_name_plural = "Password Reset Tokens"
        ordering = ["-created_at"]

    def __str__(self):
        status = "used" if self.used_at else ("expired" if self.is_expired else "active")
        return f"PasswordResetToken({self.user.email}, {status})"

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @property
    def is_valid(self) -> bool:
        return not self.is_expired and not self.is_used

    # ------------------------------------------------------------------
    # Class helpers
    # ------------------------------------------------------------------

    @classmethod
    def create_for_user(cls, user: User) -> tuple["PasswordResetToken", str]:
        """
        Generate a raw token, hash it, persist the record, and return
        (instance, raw_token).  The caller is responsible for sending
        the raw token to the user.
        """
        raw = generate_raw_token()
        instance = cls.objects.create(
            user=user,
            token_hash=hash_token(raw),
        )
        return instance, raw

    @classmethod
    def get_valid_by_raw(cls, raw_token: str):
        """
        Return a valid (not expired, not used) PasswordResetToken for
        *raw_token*, or None if no match exists.
        """
        try:
            obj = cls.objects.select_related("user").get(
                token_hash=hash_token(raw_token)
            )
        except cls.DoesNotExist:
            return None
        return obj if obj.is_valid else None

    def consume(self):
        """Mark this token as used and invalidate all other unused tokens for the same user."""
        self.used_at = timezone.now()
        self.save(update_fields=["used_at"])
        # Invalidate other unused tokens for the same user.
        PasswordResetToken.objects.filter(
            user=self.user,
            used_at__isnull=True,
        ).exclude(pk=self.pk).update(used_at=timezone.now())
