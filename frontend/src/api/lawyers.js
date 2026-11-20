/**
 * LawAid Lawyer Directory & Verification Compliance API
 * SRS: FR-2, FR-3, FR-38, NFR-4
 */
import { apiFetch, authStorage } from './http';

export async function searchLawyers(params = {}) {
  const query = new URLSearchParams();
  if (params.q) query.append('q', params.q);
  if (params.district) query.append('district', params.district);
  if (params.court) query.append('court', params.court);
  if (params.practice_area) query.append('practice_area', params.practice_area);

  const qs = query.toString();
  return await apiFetch(`/api/lawyers/${qs ? `?${qs}` : ''}`);
}

export async function getLawyerDetail(lawyerId) {
  return await apiFetch(`/api/lawyers/${lawyerId}/`);
}

/**
 * Platform Admin Verification Queue (FR-38)
 */
export async function getAdminVerificationQueue() {
  return await apiFetch('/api/lawyers/verification/queue/');
}

/**
 * Approve Lawyer Verification (FR-3, FR-38)
 */
export async function approveLawyer(lawyerId, notes = '') {
  return await apiFetch(`/api/lawyers/verification/${lawyerId}/approve/`, {
    method: 'POST',
    body: { notes },
  });
}

/**
 * Reject Lawyer Verification (FR-3, FR-38)
 */
export async function rejectLawyer(lawyerId, rejectionReason) {
  return await apiFetch(`/api/lawyers/verification/${lawyerId}/reject/`, {
    method: 'POST',
    body: { rejection_reason: rejectionReason },
  });
}

/**
 * In-Memory Decryption Document Stream (NFR-4)
 * Fetches decrypted stream with Admin Bearer Token and produces an object URL for preview.
 */
export async function fetchDecryptedDocumentBlob(documentId) {
  const token = authStorage.getToken();
  const response = await fetch(`/api/lawyers/verification/documents/${documentId}/view/`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to decrypt document: ${response.statusText}`);
  }

  const blob = await response.blob();
  const contentType = response.headers.get('content-type') || 'application/pdf';
  return {
    blobUrl: URL.createObjectURL(blob),
    contentType,
  };
}
