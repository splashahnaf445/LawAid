/**
 * LawAid Form & Display Helpers
 */

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
