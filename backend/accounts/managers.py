from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    Email is the login identifier. SRS: FR-1, FR-4.

    is_active / is_staff / is_superuser are not columns in db/schema.sql; the User model
    derives them from `status` and `role`, so they are never passed to the model here.
    """
    def create_user(self, email, full_name, password=None, role='client', **extra_fields):
        if not email:
            raise ValueError('Email address is required.')
        if not full_name:
            raise ValueError('Full name is required.')

        # Drop Django-style flags that don't exist as columns.
        for flag in ('is_active', 'is_staff', 'is_superuser'):
            extra_fields.pop(flag, None)

        email = self.normalize_email(email.strip()).lower()

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
        extra_fields['role'] = 'admin'
        return self.create_user(email, full_name, password, **extra_fields)