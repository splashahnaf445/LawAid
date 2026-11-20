import os
import uuid
import hashlib
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from cryptography.fernet import Fernet, InvalidToken

class DocumentEncryptionService:
    """
    Handles secure encryption-at-rest and on-the-fly in-memory decryption
    for sensitive identification files (NID cards and Bar Council certificates).
    
    SRS Compliance:
    - FR-2: Lawyer NID and Bar Council certificate upload during registration.
    - NFR-1: Encrypt sensitive personal identification data at rest.
    - NFR-4: Files stored encrypted and visible only to admins during verification.
    """
    _cipher = None

    @classmethod
    def get_cipher(cls) -> Fernet:
        if cls._cipher is None:
            raw_key = getattr(settings, 'DOCUMENT_ENCRYPTION_KEY', None)
            if not raw_key:
                # Default fallback dev key if not provided in environment
                raw_key = 'c1nwgexw36iltaDC_aCA64MHK2AkBmvxoJK0YdQ4GZY='
            if isinstance(raw_key, str):
                raw_key = raw_key.encode('utf-8')
            try:
                cls._cipher = Fernet(raw_key)
            except Exception as exc:
                raise ImproperlyConfigured(f"Invalid DOCUMENT_ENCRYPTION_KEY: {exc}")
        return cls._cipher

    @classmethod
    def encrypt_bytes(cls, plaintext: bytes) -> bytes:
        """Encrypts bytes using authenticated symmetric encryption (Fernet AES-128-CBC + HMAC)."""
        return cls.get_cipher().encrypt(plaintext)

    @classmethod
    def decrypt_bytes(cls, ciphertext: bytes) -> bytes:
        """Decrypts bytes, verifying HMAC authentication tag."""
        try:
            return cls.get_cipher().decrypt(ciphertext)
        except InvalidToken as exc:
            raise ValueError("Decryption failed: corrupted ciphertext or invalid secret key.") from exc

    @classmethod
    def save_encrypted_file(cls, uploaded_file, lawyer_id: str, doc_type: str) -> dict:
        """
        Reads uploaded file content, encrypts it, and saves only the encrypted ciphertext to disk.
        Returns document metadata dict for database persistence.
        """
        storage_dir = getattr(
            settings, 
            'ENCRYPTED_DOCUMENTS_DIR', 
            os.path.join(settings.BASE_DIR, 'storage', 'encrypted_documents')
        )
        os.makedirs(storage_dir, exist_ok=True)

        original_filename = getattr(uploaded_file, 'name', f"{doc_type}_{uuid.uuid4().hex[:8]}")
        content_type = getattr(uploaded_file, 'content_type', 'application/pdf')

        raw_bytes = uploaded_file.read() if hasattr(uploaded_file, 'read') else bytes(uploaded_file)
        file_size = len(raw_bytes)
        checksum = hashlib.sha256(raw_bytes).hexdigest()

        # Encrypt the raw content
        encrypted_bytes = cls.encrypt_bytes(raw_bytes)

        # Generate secure obfuscated filename for disk storage
        secure_filename = f"{lawyer_id}_{doc_type}_{uuid.uuid4().hex}.enc"
        file_path = os.path.join(storage_dir, secure_filename)

        with open(file_path, 'wb') as f:
            f.write(encrypted_bytes)

        # Uniform file_url matching schema.sql pattern
        file_url = f"private://verification/{doc_type}/{secure_filename}"

        return {
            'file_path': file_path,
            'file_url': file_url,
            'original_filename': original_filename,
            'mime_type': content_type,
            'file_size_bytes': file_size,
            'sha256_checksum': checksum,
        }

    @classmethod
    def read_and_decrypt_file(cls, file_path_or_url: str) -> bytes:
        """
        Reads the encrypted file from disk and returns decrypted raw bytes in memory.
        No plaintext file is ever written to disk or exposed to the public.
        """
        path = file_path_or_url
        if path.startswith('private://verification/'):
            # Resolve relative to ENCRYPTED_DOCUMENTS_DIR
            filename = os.path.basename(path)
            storage_dir = getattr(
                settings, 
                'ENCRYPTED_DOCUMENTS_DIR', 
                os.path.join(settings.BASE_DIR, 'storage', 'encrypted_documents')
            )
            path = os.path.join(storage_dir, filename)

        if not os.path.exists(path):
            raise FileNotFoundError(f"Encrypted document file not found at: {path}")

        with open(path, 'rb') as f:
            encrypted_content = f.read()

        return cls.decrypt_bytes(encrypted_content)
