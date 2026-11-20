from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Email-based login (no username). Role strings are literal to avoid a circular import."""

    def _create(self, email, password, **extra):
        if not email:
            raise ValueError("An email address is required.")
        user = self.model(email=email.strip().lower(), **extra)
        user.set_password(password)  # None -> unusable password
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("role", "client")
        return self._create(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra["role"] = "admin"
        return self._create(email, password, **extra)
