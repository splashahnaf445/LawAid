/**
 * LawAid Client-Side Validation Utilities
 * Matching Django Backend Specifications (SRS FR-1, FR-2, NFR-4)
 */

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
