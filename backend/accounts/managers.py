from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom user manager where email is the primary identifier for authentication.
    SRS: FR-1, FR-4.

    Integration note: Ahnaf's manager (staff/superuser flags, unusable passwords) with
    Usama's email normalisation (trim + lower-case). Both call styles work:
    create_user(email=..., password=..., role=..., full_name=...).
    """
    def create_user(self, email, full_name, password=None, role='client', **extra_fields):
        if not email:
            raise ValueError('Email address is required.')
        if not full_name:
            raise ValueError('Full name is required.')

        email = self.normalize_email(email.strip()).lower()
        extra_fields.setdefault('is_active', True)

        user = self.model(
            email=email,
            full_name=full_name,
            role=role,
            **extra_fields
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, full_name, password, **extra_fields)
