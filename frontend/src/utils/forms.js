/**
 * Turn an axios error into { fields, general }.
 *  - fields:  { fieldName: 'message' } for DRF 400 responses ({ email: ["..."] })
 *  - general: a message for everything that is not tied to a visible field
 * Fields not in `knownFields` are folded into `general` so no error is ever swallowed.
 */
export function parseApiError(err, knownFields = []) {
  const res = err?.response
  if (!res) return { fields: {}, general: 'Cannot reach the server. Check your connection and try again.' }
  if (res.status === 429) {
    return { fields: {}, general: 'Too many attempts. Please wait a while and try again.' }
  }
  if (res.status === 400 && res.data && typeof res.data === 'object') {
    const fields = {}
    const general = []
    for (const [key, value] of Object.entries(res.data)) {
      const message = Array.isArray(value) ? value.join(' ') : String(value)
      if (knownFields.includes(key)) fields[key] = message
      else general.push(message)
    }
    return { fields, general: general.join(' ') }
  }
  return { fields: {}, general: 'Something went wrong on our side. Please try again.' }
}

// ---------------------------------------------------------------------------
// Ahnaf (SYS-21): helpers used by the verification pages (DocumentDropzone,
// AdminVerification, Login). Kept from feature/lawyer-verification-and-badge.
// ---------------------------------------------------------------------------

export function formatFileSize(bytes) {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

export function formatDate(dateString) {
  if (!dateString) return 'N/A';
  try {
    const d = new Date(dateString);
    return d.toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  } catch (e) {
    return dateString;
  }
}

export function extractErrorMessage(errorResponse, fallbackMessage = 'An unexpected error occurred.') {
  if (!errorResponse) return fallbackMessage;
  if (typeof errorResponse === 'string') return errorResponse;
  if (errorResponse.detail) return errorResponse.detail;
  if (errorResponse.message) return errorResponse.message;

  // DRF field validation error dictionary: {"field": ["msg"]}
  const keys = Object.keys(errorResponse);
  if (keys.length > 0) {
    const firstKey = keys[0];
    const val = errorResponse[firstKey];
    if (Array.isArray(val)) {
      return `${firstKey.replace(/_/g, ' ')}: ${val[0]}`;
    }
    if (typeof val === 'string') {
      return `${firstKey.replace(/_/g, ' ')}: ${val}`;
    }
  }
  return fallbackMessage;
}
