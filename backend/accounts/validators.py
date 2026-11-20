import re
from django.core.exceptions import ValidationError

BD_PHONE_REGEX = re.compile(r'^\+8801[3-9][0-9]{8}$')
BAR_COUNCIL_REGEX = re.compile(r'^[A-Za-z0-9\-\/]{3,30}$')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB

def normalize_bd_phone(phone_str: str) -> str:
    """Normalizes Bangladeshi phone numbers into +8801XXXXXXXXX format."""
    cleaned = re.sub(r'[\s\-()]', '', phone_str.strip())
    if cleaned.startswith('01') and len(cleaned) == 11:
        cleaned = '+88' + cleaned
    elif cleaned.startswith('8801') and len(cleaned) == 13:
        cleaned = '+' + cleaned
    return cleaned

def validate_bd_phone(value: str):
    normalized = normalize_bd_phone(value)
    if not BD_PHONE_REGEX.match(normalized):
        raise ValidationError(
            f"'{value}' is not a valid Bangladeshi mobile number. Format must be +8801XXXXXXXXX."
        )

def validate_bar_council_no(value: str):
    cleaned = value.strip().upper()
    if not BAR_COUNCIL_REGEX.match(cleaned):
        raise ValidationError(
            f"'{value}' is not a valid Bar Council ID format. Allowed characters: letters, digits, dash, slash."
        )

def validate_verification_document(file_obj):
    """
    Validates uploaded file format and size for NID and Bar Council Certificate (FR-2).
    """
    if not file_obj:
        raise ValidationError("File is required.")

    filename = getattr(file_obj, 'name', '')
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"Unsupported file type (.{ext}). Allowed formats are PDF, PNG, JPG, and JPEG."
        )

    file_size = getattr(file_obj, 'size', 0)
    if file_size > MAX_FILE_SIZE_BYTES:
        raise ValidationError(
            f"File size exceeds maximum limit of 15MB (file size: {file_size / (1024*1024):.2f}MB)."
        )
