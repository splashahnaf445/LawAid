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
                raise ImproperlyConfigured(
                    "DOCUMENT_ENCRYPTION_KEY is missing from Django settings or environment."
                )
            if isinstance(raw_key, str):
                raw_key = raw_key.encode('utf-8')
            try:
                cls._cipher = Fernet(raw_key)
            except Exception as exc:
                raise ImproperlyConfigured(
                    f"Invalid DOCUMENT_ENCRYPTION_KEY provided: {exc}"
                )
        return cls._cipher

    @classmethod
    def encrypt_bytes(cls, plaintext: bytes) -> bytes:
        """Encrypts bytes using authenticated symmetric encryption (Fernet AES-128-CBC + HMAC)."""
        cipher = cls.get_cipher()
        return cipher.encrypt(plaintext)

    @classmethod
    def decrypt_bytes(cls, ciphertext: bytes) -> bytes:
        """Decrypts bytes, verifying HMAC authentication tag."""
        cipher = cls.get_cipher()
        try:
            return cipher.decrypt(ciphertext)
        except InvalidToken as exc:
            raise ValueError("Decryption failed: invalid token or corrupted ciphertext.") from exc

    @classmethod
    def save_encrypted_file(cls, uploaded_file, lawyer_id: str, doc_type: str) -> dict:
        """
        Reads uploaded file content, encrypts it, and saves only the encrypted ciphertext to disk.
        Returns document metadata dict for database persistence.
        """
        # Ensure storage directory exists
        storage_dir = getattr(settings, 'ENCRYPTED_DOCUMENTS_DIR', os.path.join(settings.BASE_DIR, 'storage', 'encrypted_documents'))
        os.makedirs(storage_dir, exist_ok=True)

        original_filename = getattr(uploaded_file, 'name', f"{doc_type}_{uuid.uuid4().hex[:8]}")
        content_type = getattr(uploaded_file, 'content_type', 'application/octet-stream')
        
        # Read raw content
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

        return {
            'file_path': file_path,
            'original_filename': original_filename,
            'mime_type': content_type,
            'file_size_bytes': file_size,
            'sha256_checksum': checksum,
        }

    @classmethod
    def read_and_decrypt_file(cls, file_path: str) -> bytes:
        """
        Reads the encrypted file from disk and returns decrypted raw bytes in memory.
        No plaintext file is ever written to disk.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Encrypted document file not found at path: {file_path}")

        with open(file_path, 'rb') as f:
            encrypted_content = f.read()

        return cls.decrypt_bytes(encrypted_content)
