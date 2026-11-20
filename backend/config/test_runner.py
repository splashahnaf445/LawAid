"""
Test runner that builds the real schema.

Our models are unmanaged, so Django's migrations never create the tables. After
Django creates the empty test database we load db/schema.sql into it, so tests
exercise the real constraints (citext email, phone CHECK, composite role FKs...).
Requires PostgreSQL 18 (schema uses uuidv7()) and CREATEDB privilege.
"""
from django.conf import settings
from django.db import connections
from django.test.runner import DiscoverRunner


class SchemaTestRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        config = super().setup_databases(**kwargs)
        sql = settings.LAWAID_SCHEMA_SQL.read_text(encoding="utf-8")
        for alias in connections:
            conn = connections[alias]
            if conn.vendor == "postgresql":
                with conn.cursor() as cursor:
                    cursor.execute(sql)  # no params -> '%' in plpgsql messages is left alone
        return config