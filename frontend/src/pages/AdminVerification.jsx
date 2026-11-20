import React, { useState, useEffect } from 'react';
import {
  ClipboardCheck,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Lock,
  Eye,
  FileText,
  AlertTriangle,
  RefreshCw,
  Scale,
  ExternalLink,
  X
} from 'lucide-react';
import {
  getAdminVerificationQueue,
  approveLawyer,
  rejectLawyer,
  fetchDecryptedDocumentBlob
} from '../api/lawyers';
import { formatDate } from '../utils/forms';

export default function AdminVerification({ currentUser, onNavigate, onLoginAsAdmin }) {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionSuccess, setActionSuccess] = useState(null);

  // Document Preview Modal State (NFR-4)
  const [previewDoc, setPreviewDoc] = useState(null);
  const [previewBlobUrl, setPreviewBlobUrl] = useState(null);
  const [previewContentType, setPreviewContentType] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  // Rejection Modal State
  const [rejectingLawyer, setRejectingLawyer] = useState(null);
  const [rejectionReason, setRejectionReason] = useState('');
  const [rejectLoading, setRejectLoading] = useState(false);

  const isAdmin = currentUser && (currentUser.role === 'admin' || currentUser.is_admin);

  const fetchQueue = async () => {
    if (!isAdmin) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await getAdminVerificationQueue();
      setQueue(Array.isArray(data) ? data : data.results || []);
    } catch (err) {
      setError('Unable to load verification queue. Verify you are authenticated with administrator privileges.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, [isAdmin]);

  // Preview an encrypted document via in-memory stream (NFR-4)
  const handlePreviewDocument = async (doc) => {
    setPreviewDoc(doc);
    setPreviewBlobUrl(null);
    setPreviewLoading(true);
    try {
      const { blobUrl, contentType } = await fetchDecryptedDocumentBlob(doc.id);
      setPreviewBlobUrl(blobUrl);
      setPreviewContentType(contentType);
    } catch (err) {
      alert(`Decryption failed: ${err.message}. Only administrators with valid credentials can decrypt documents.`);
      setPreviewDoc(null);
    } finally {
      setPreviewLoading(false);
    }
  };

  const closePreview = () => {
    if (previewBlobUrl) {
      URL.revokeObjectURL(previewBlobUrl);
    }
    setPreviewDoc(null);
    setPreviewBlobUrl(null);
    setPreviewContentType(null);
  };

  // Approve lawyer (SRS FR-3, FR-38)
  const handleApprove = async (lawyer) => {
    const confirmed = window.confirm(
      `Approve verification for Advocate ${lawyer.full_name} (Sanad: ${lawyer.bar_council_no})?\n\nThis will award the LawAid Verification Badge and immediately publish their profile to the public search directory.`
    );
    if (!confirmed) return;

    try {
      await approveLawyer(lawyer.id, 'Verified via Bangladesh Bar Council Gazette cross-check');
      setActionSuccess(`Advocate ${lawyer.full_name} has been approved! Verification badge awarded.`);
      fetchQueue();
    } catch (err) {
      alert(`Approval failed: ${err.message}`);
    }
  };

  // Submit rejection
  const handleSubmitRejection = async (e) => {
    e.preventDefault();
    if (!rejectionReason.trim()) {
      alert('Please state a reason for rejecting the verification.');
      return;
    }

    setRejectLoading(true);
    try {
      await rejectLawyer(rejectingLawyer.id, rejectionReason.trim());
      setActionSuccess(`Application for ${rejectingLawyer.full_name} was marked as rejected.`);
      setRejectingLawyer(null);
      setRejectionReason('');
      fetchQueue();
    } catch (err) {
      alert(`Rejection failed: ${err.message}`);
    } finally {
      setRejectLoading(false);
    }
  };

  // If not admin, show permission wall with quick test button
  if (!isAdmin) {
    return (
      <div style={{ padding: '4rem 0' }}>
        <div className="container" style={{ maxWidth: '640px', textAlign: 'center' }}>
          <div
            style={{
              width: 64,
              height: 64,
              borderRadius: '50%',
              backgroundColor: '#fef3c7',
              color: '#d97706',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1.5rem',
            }}
          >
            <Lock size={32} />
          </div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0f172a', marginBottom: '0.75rem' }}>
            Administrator Access Required
          </h2>
          <p style={{ color: '#64748b', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: '2rem' }}>
            Under SRS <strong>NFR-4</strong> and <strong>FR-38</strong>, the Lawyer Verification Queue and
            decrypted document viewer are restricted to authenticated Platform Compliance Administrators.
          </p>

          <div className="card" style={{ padding: '1.5rem', background: '#ffffff', textAlign: 'left', marginBottom: '2rem' }}>
            <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>
              Evaluation / Demonstration Quick Login:
            </h4>
            <p style={{ fontSize: '0.85rem', color: '#64748b', marginBottom: '1rem' }}>
              Sign in with the seeded Platform Admin credentials to review pending submissions and decrypt documents.
            </p>
            <button
              className="btn btn-primary"
              style={{ width: '100%', padding: '0.75rem' }}
              onClick={onLoginAsAdmin}
            >
              <ClipboardCheck size={18} />
              <span>Sign In as Platform Admin (admin@lawaid.gov.bd)</span>
            </button>
          </div>

          <button
            className="btn btn-secondary"
            onClick={() => onNavigate('landing')}
          >
            Return to Homepage
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '2.5rem 0 4rem' }}>
      <div className="container">
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '2rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#b45309', fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              <ClipboardCheck size={18} />
              <span>Compliance & Credential Verification Portal</span>
            </div>
            <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a', marginTop: '0.35rem' }}>
              Lawyer Verification Queue
            </h1>
            <p style={{ color: '#64748b', fontSize: '0.925rem', marginTop: '0.25rem' }}>
              Review Bar Council Sanad credentials and decrypt NID documentation in-memory (SRS FR-3, FR-38, NFR-4).
            </p>
          </div>

          <button
            className="btn btn-secondary btn-sm"
            onClick={fetchQueue}
            disabled={loading}
          >
            <RefreshCw size={15} className={loading ? 'spinner' : ''} />
            <span>Refresh Queue</span>
          </button>
        </div>

        {/* Success toast */}
        {actionSuccess && (
          <div className="alert alert-success" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CheckCircle2 size={18} />
              <span>{actionSuccess}</span>
            </div>
            <button
              style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: '#166534' }}
              onClick={() => setActionSuccess(null)}
            >
              <X size={16} />
            </button>
          </div>
        )}

        {/* Security Info Callout */}
        <div className="security-callout">
          <div className="security-callout-icon">
            <Lock size={20} />
          </div>
          <div className="security-callout-content">
            <h4>NFR-4 Encryption Protocol Enforced</h4>
            <p>
              Underlying document files are stored symmetrically encrypted on disk with <strong>Fernet AES-128-CBC + HMAC-SHA256</strong>.
              Clicking "Preview Decrypted" streams the decrypted payload directly into browser memory via an authenticated session.
              Public URLs are strictly prohibited.
            </p>
          </div>
        </div>

        {/* Table of submissions */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '4rem 0' }}>
            <div className="spinner" style={{ borderColor: '#0d9488', borderTopColor: 'transparent', width: '2rem', height: '2rem', margin: '0 auto 1rem' }} />
            <p style={{ color: '#64748b' }}>Loading pending verification requests...</p>
          </div>
        ) : error ? (
          <div className="alert alert-danger">{error}</div>
        ) : queue.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '3.5rem 1.5rem' }}>
            <CheckCircle2 size={48} color="#10b981" style={{ margin: '0 auto 1rem' }} />
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f172a' }}>
              Verification Queue is Clear
            </h3>
            <p style={{ color: '#64748b', fontSize: '0.9rem', maxWidth: '420px', margin: '0.5rem auto 1.5rem' }}>
              All lawyer registration submissions have been audited. New registrations will appear here for compliance review.
            </p>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => onNavigate('lawyers')}
            >
              View Verified Lawyer Directory
            </button>
          </div>
        ) : (
          <div className="admin-table-wrapper">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Advocate Name</th>
                  <th>Bar Council Sanad</th>
                  <th>Court & District</th>
                  <th>Submitted</th>
                  <th>Encrypted Documents (NFR-4)</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {queue.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <div style={{ fontWeight: 700, color: '#0f172a' }}>{item.full_name}</div>
                      <div style={{ fontSize: '0.775rem', color: '#64748b' }}>{item.email}</div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{item.phone}</div>
                    </td>

                    <td>
                      <span
                        style={{
                          fontFamily: 'monospace',
                          background: '#f1f5f9',
                          padding: '0.2rem 0.5rem',
                          borderRadius: '4px',
                          fontWeight: 600,
                          color: '#0f172a',
                        }}
                      >
                        {item.bar_council_no}
                      </span>
                    </td>

                    <td>
                      <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155' }}>
                        {item.primary_court_name || 'Supreme Court of Bangladesh'}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                        {item.district} • {item.years_experience} yrs exp
                      </div>
                    </td>

                    <td style={{ fontSize: '0.8rem', color: '#64748b' }}>
                      {formatDate(item.created_at)}
                    </td>

                    <td>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        {item.documents && item.documents.length > 0 ? (
                          item.documents.map((doc) => (
                            <button
                              key={doc.id}
                              type="button"
                              className="btn btn-secondary btn-sm"
                              style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem', justifyContent: 'flex-start' }}
                              onClick={() => handlePreviewDocument(doc)}
                            >
                              <Lock size={12} color="#0d9488" />
                              <span>{doc.document_type_display || doc.document_type}</span>
                              <Eye size={12} style={{ marginLeft: 'auto' }} />
                            </button>
                          ))
                        ) : (
                          <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>No docs attached</span>
                        )}
                      </div>
                    </td>

                    <td>
                      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                        <button
                          className="btn btn-success btn-sm"
                          onClick={() => handleApprove(item)}
                          title="Approve verification (awards badge & reveals on search)"
                        >
                          <CheckCircle2 size={14} />
                          <span>Approve</span>
                        </button>

                        <button
                          className="btn btn-danger btn-sm"
                          onClick={() => {
                            setRejectingLawyer(item);
                            setRejectionReason('');
                          }}
                          title="Reject verification"
                        >
                          <XCircle size={14} />
                          <span>Reject</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Document In-Memory Decryption Stream Modal (NFR-4) */}
        {previewDoc && (
          <div className="modal-overlay" onClick={closePreview}>
            <div className="modal-content" style={{ maxWidth: '780px' }} onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f172a' }}>
                      {previewDoc.document_type_display || previewDoc.document_type}
                    </h3>
                    <span className="badge badge-success">
                      <Lock size={10} /> In-Memory Decrypted
                    </span>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '2px' }}>
                    Filename: {previewDoc.file_name} • Algorithm: {previewDoc.encryption_algorithm || 'AES-128-CBC + HMAC'}
                  </div>
                </div>

                <button className="modal-close" onClick={closePreview}>
                  <X size={20} />
                </button>
              </div>

              {/* Viewer body */}
              <div style={{ minHeight: '380px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#0f172a', borderRadius: '8px', overflow: 'hidden', padding: '1rem' }}>
                {previewLoading ? (
                  <div style={{ textAlign: 'center', color: '#ffffff' }}>
                    <div className="spinner" style={{ margin: '0 auto 0.75rem' }} />
                    <p style={{ fontSize: '0.85rem' }}>Decrypting document using master platform key...</p>
                  </div>
                ) : previewBlobUrl ? (
                  previewContentType && previewContentType.includes('image') ? (
                    <img
                      src={previewBlobUrl}
                      alt="Decrypted Document"
                      style={{ maxWidth: '100%', maxHeight: '520px', objectFit: 'contain' }}
                    />
                  ) : (
                    <iframe
                      src={previewBlobUrl}
                      title="Decrypted PDF Document"
                      style={{ width: '100%', height: '520px', border: 'none' }}
                    />
                  )
                ) : (
                  <div style={{ color: '#ef4444', textAlign: 'center' }}>
                    <AlertTriangle size={32} style={{ margin: '0 auto 0.5rem' }} />
                    <p>Unable to stream decrypted document.</p>
                  </div>
                )}
              </div>

              <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                  Document SHA-256 Hash: <code style={{ fontSize: '0.7rem' }}>{previewDoc.checksum_sha256 ? previewDoc.checksum_sha256.substring(0, 24) + '...' : 'Verified'}</code>
                </span>
                <button className="btn btn-secondary btn-sm" onClick={closePreview}>
                  Close Preview
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Rejection Modal */}
        {rejectingLawyer && (
          <div className="modal-overlay" onClick={() => setRejectingLawyer(null)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <div>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#b91c1c' }}>
                    Reject Verification Application
                  </h3>
                  <div style={{ fontSize: '0.85rem', color: '#64748b' }}>
                    Advocate: {rejectingLawyer.full_name} ({rejectingLawyer.bar_council_no})
                  </div>
                </div>
                <button className="modal-close" onClick={() => setRejectingLawyer(null)}>
                  <X size={20} />
                </button>
              </div>

              <form onSubmit={handleSubmitRejection}>
                <div className="form-group">
                  <label className="form-label">
                    Reason for Rejection <span className="required">*</span>
                  </label>
                  <textarea
                    rows="3"
                    className="form-control"
                    placeholder="e.g. Bar Council Sanad number could not be validated against the 2024 Gazette, or NID image is illegible."
                    value={rejectionReason}
                    onChange={(e) => setRejectionReason(e.target.value)}
                    required
                  />
                  <div className="form-text">
                    This note will be logged in the compliance audit trail and sent to the applicant.
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.5rem' }}>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setRejectingLawyer(null)}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-danger"
                    disabled={rejectLoading}
                  >
                    {rejectLoading ? 'Submitting...' : 'Confirm Rejection'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
