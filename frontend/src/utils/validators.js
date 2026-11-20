// Client-side mirror of backend/accounts/validators.py. These give instant feedback;
// the server is still the source of truth and re-validates everything.
// Every validate* function returns an error string, or '' when the value is fine.

export const PHONE_ERROR = 'Enter a valid Bangladesh mobile number, e.g. +8801712345678.'
export const BAR_NO_ERROR = 'Enter a valid Bar Council number, e.g. SC-7841 or BC-2018-9412.'
export const BAR_COUNCIL_RE = /^[A-Z]{2,5}-(?:\d{4}-)?\d{3,6}$/

/** '+880 1712-345678' | '01712345678' -> '+8801712345678', or null if invalid. */
export function normalizePhone(raw) {
  const s = (raw || '').replace(/[\s\-().]/g, '')
  let tail
  if (s.startsWith('+880')) tail = s.slice(4)
  else if (s.startsWith('880')) tail = s.slice(3)
  else if (s.startsWith('0')) tail = s.slice(1)
  else return null
  return /^1[3-9]\d{8}$/.test(tail) ? `+880${tail}` : null
}

export function normalizeBarCouncilNo(raw) {
  return (raw || '').trim().toUpperCase().replace(/\s*-\s*/g, '-')
}

export const validateFullName = (v) =>
  v.trim().length >= 2 && /\p{L}/u.test(v) ? '' : 'Enter your full name.'

export const validateEmail = (v) =>
  /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim()) ? '' : 'Enter a valid email address.'

export function validatePhone(v, { required }) {
  if (!v.trim()) return required ? 'Enter your mobile number.' : ''
  return normalizePhone(v) ? '' : PHONE_ERROR
}

export const validateBarCouncilNo = (v) =>
  BAR_COUNCIL_RE.test(normalizeBarCouncilNo(v)) ? '' : BAR_NO_ERROR

export const validateFee = (v) =>
  !v.trim() || /^\d{1,8}(\.\d{1,2})?$/.test(v.trim()) ? '' : 'Enter an amount in BDT, e.g. 1500.'

export function passwordChecks(pw) {
  return {
    length: pw.length >= 8,
    lower: /[a-z]/.test(pw),
    upper: /[A-Z]/.test(pw),
    digit: /\d/.test(pw),
    special: /[^A-Za-z0-9]/.test(pw),
  }
}

/** 0-4: length, mixed case, number, special character. Drives the strength meter. */
export function passwordScore(pw) {
  if (!pw) return 0
  const c = passwordChecks(pw)
  return [c.length, c.lower && c.upper, c.digit, c.special].filter(Boolean).length
}

export function validatePassword(pw) {
  if (!pw) return 'Create a password.'
  const c = passwordChecks(pw)
  if (!c.length) return 'Use at least 8 characters.'
  if (!c.lower || !c.upper) return 'Use both upper and lower case letters.'
  if (!c.digit) return 'Add a number.'
  if (!c.special) return 'Add a special character (e.g. @ # $ !).'
  return ''
}

export const validateConfirm = (pw, confirm) => (pw === confirm ? '' : 'Passwords do not match.')

// ---------------------------------------------------------------------------
// Ahnaf (SYS-21): helpers used by the verification pages (DocumentDropzone,
// AdminVerification, Login). Kept from feature/lawyer-verification-and-badge.
// ---------------------------------------------------------------------------

export const PHONE_REGEX = /^(?:\+?8801|01)[3-9]\d{8}$/;
export const SANAD_REGEX = /^\d{1,6}\/\d{4}$/;
export const ALLOWED_MIME_TYPES = ['application/pdf', 'image/jpeg', 'image/png'];
export const MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024; // 15MB

/**
 * Normalizes BD phone numbers to +8801XXXXXXXXX standard
 */
export function normalizeBdPhone(phone) {
  if (!phone) return '';
  let clean = phone.replace(/[\s\-\(\)]/g, '');
  if (clean.startsWith('8801')) {
    clean = '+' + clean;
  } else if (clean.startsWith('01')) {
    clean = '+88' + clean;
  }
  return clean;
}

/**
 * Validates Bangladesh mobile numbers (+88013.. to +88019..)
 */
export function validateBdPhone(phone) {
  if (!phone) return 'Phone number is required.';
  const normalized = normalizeBdPhone(phone);
  if (!PHONE_REGEX.test(normalized)) {
    return 'Invalid Bangladeshi phone number. Expected +8801XXXXXXXXX or 01XXXXXXXXX.';
  }
  return null;
}

/**
 * Validates Bar Council Sanad Number format: <number>/<year>
 */
export function validateBarCouncilSanad(sanad) {
  if (!sanad) return 'Bar Council Sanad number is required.';
  const trimmed = sanad.trim();
  if (!SANAD_REGEX.test(trimmed)) {
    return 'Invalid Sanad format. Must be <EnrollmentNumber>/<Year> (e.g. 14205/2018).';
  }
  const year = parseInt(trimmed.split('/')[1], 10);
  const currentYear = new Date().getFullYear();
  if (year < 1971 || year > currentYear) {
    return `Enrollment year must be between 1971 and ${currentYear}.`;
  }
  return null;
}

/**
 * Validates document upload type (PDF, JPEG, PNG) and size (<= 15MB)
 */
export function validateDocumentFile(file, docTypeLabel = 'Document') {
  if (!file) {
    return `${docTypeLabel} is required for verification.`;
  }
  if (!ALLOWED_MIME_TYPES.includes(file.type)) {
    return `${docTypeLabel} must be a PDF, JPG, or PNG file.`;
  }
  if (file.size > MAX_FILE_SIZE_BYTES) {
    const sizeMb = (file.size / (1024 * 1024)).toFixed(1);
    return `${docTypeLabel} size (${sizeMb} MB) exceeds maximum allowed limit of 15 MB.`;
  }
  return null;
}
