
import uuid

from django.db import models
from django.utils import timezone


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20)                  
    full_name = models.TextField()
    email = models.CharField(max_length=254)              
    phone = models.TextField(null=True, blank=True)
    avatar_url = models.TextField(null=True, blank=True)
    password_hash = models.TextField()
    preferred_language = models.CharField(max_length=2, default="bn")
    status = models.CharField(max_length=30, default="active")
    two_factor_enabled = models.BooleanField(default=False)
    last_login_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "users"

    
    is_authenticated = True
    is_anonymous = False

    @property
    def can_sign_in(self):
        return self.status == "active" and self.deleted_at is None


class RefreshToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column="user_id", related_name="+")
    token_hash = models.TextField(unique=True)              
    user_agent = models.TextField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = "refresh_tokens"
