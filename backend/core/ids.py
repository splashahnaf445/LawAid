import os
import time
import uuid


def uuid7() -> uuid.UUID:
    """RFC 9562 UUIDv7 (time-ordered), matching the schema's uuidv7() primary keys.

    Generated in Python so the app knows the id before INSERT and works on any
    supported Python version (uuid.uuid7 only exists in 3.14+).
    """
    ts_ms = time.time_ns() // 1_000_000
    rand = int.from_bytes(os.urandom(10), "big")  # 80 random bits
    rand_a = rand >> 68                           # 12 bits
    rand_b = rand & ((1 << 62) - 1)               # 62 bits
    value = ((ts_ms & ((1 << 48) - 1)) << 80) | (0x7 << 76) | (rand_a << 64) | (0b10 << 62) | rand_b
    return uuid.UUID(int=value)