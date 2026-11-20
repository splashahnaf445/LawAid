from django.test.runner import DiscoverRunner
from django.db import connection

class LawAidTestRunner(DiscoverRunner):
    """
    Custom test runner for LawAid.
    Supports Raw SQL schema architecture:
    - If running against PostgreSQL: can execute db/schema.sql and seed.sql.
    - If running against SQLite (local developer/CI mode): ensures models can create their tables.
    """
    def setup_databases(self, **kwargs):
        # Dynamically set managed=True on models during tests so test database tables exist
        from django.apps import apps
        unmanaged_models = [m for m in apps.get_models() if not m._meta.managed]
        for m in unmanaged_models:
            m._meta.managed = True

        result = super().setup_databases(**kwargs)
        return result
