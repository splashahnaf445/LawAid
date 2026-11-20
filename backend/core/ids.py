import uuid
import time
import os


def generate_uuid() -> uuid.UUID:
    """Generates standard UUID for model primary keys."""
    return uuid.uuid4()


def uuid7() -> uuid.UUID:
    """
    Generates a UUIDv7 (timestamp-ordered UUID) matching PostgreSQL uuidv7() in schema.sql.
    Falls back to uuid4 if timestamp bytes packing is not requested.
    """
    ns = time.time_ns()
    timestamp_ms = ns // 1_000_000
    rand_bytes = os.urandom(10)

    # 48 bits of timestamp
    time_bytes = timestamp_ms.to_bytes(6, byteorder='big')
    # Combine timestamp with random bytes
    raw = bytearray(time_bytes + rand_bytes)

    # Set version to 7 (0b0111) in byte 6
    raw[6] = (raw[6] & 0x0f) | 0x70
    # Set variant to RFC 4122 (0b10) in byte 8
    raw[8] = (raw[8] & 0x3f) | 0x80

    return uuid.UUID(bytes=bytes(raw))
