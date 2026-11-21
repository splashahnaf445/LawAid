"""
One-off repair for a database built from db/schema.sql + db/seed.sql.
Run:  python manage.py shell < fix_db.py     (safe to run more than once)

1. Seed passwords are pgcrypto bcrypt hashes ('$2a$08$...'). Django's BCryptPasswordHasher
   expects 'bcrypt$' + hash  ->  'bcrypt$$2a$08$...'  (two dollar signs).
   The previous version wrote 'bcrypt' + hash (one dollar sign), which never verifies.
2. Adds the client_profiles columns the models use.
"""
from django.db import connection

with connection.cursor() as k:
    # repair hashes written by the old, broken script ('bcrypt$2a$...' -> 'bcrypt$$2a$...')
    k.execute("UPDATE users SET password_hash = 'bcrypt$' || substr(password_hash, 7) "
              "WHERE password_hash LIKE 'bcrypt$2%'")
    print("broken hashes repaired:", k.rowcount)

    # raw pgcrypto hashes -> Django format
    k.execute("UPDATE users SET password_hash = 'bcrypt$' || password_hash WHERE password_hash LIKE '$2%'")
    print("raw hashes converted:", k.rowcount)

    k.execute("""
        ALTER TABLE client_profiles
          ADD COLUMN IF NOT EXISTS nid_number text,
          ADD COLUMN IF NOT EXISTS emergency_contact text,
          ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now(),
          ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now()
    """)
    print("client_profiles columns ensured")

    k.execute("SELECT left(password_hash, 16) FROM users LIMIT 1")
    print(k.fetchall())
