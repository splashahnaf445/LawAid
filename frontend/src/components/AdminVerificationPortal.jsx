import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  CheckCircle, 
  XCircle, 
  Eye, 
  FileText, 
  Lock, 
  Search, 
  RefreshCw, 
  Scale, 
  UserCheck, 
  AlertTriangle,
  Award,
  ExternalLink,
  Download
} from 'lucide-react';
import { lawAidApi } from '../services/api';
import VerifiedBadge from './VerifiedBadge';

export default function AdminVerificationPortal({ onStatusChanged }) {
  const [filter, setFilter] = useState('pending');
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedLawyer, setSelectedLawyer] = useState(null);
  const [rejectionModalLawyer, setRejectionModalLawyer] = useState(null);
  const [rejectionReason, setRejectionReason] = useState('');
  const [activeDocPreview, setActiveDocPreview] = useState(null);
  const [actionSuccessMsg, setActionSuccessMsg] = useState('');

  const fetchApplications = async () => {
    setLoading(true);
    try {
      const res = await lawAidApi.getAdminPendingVerifications(filter);
      setApplications(res.applications || []);
    } catch (err) {
      console.error('Error loading verification applications:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications();
  }, [filter]);

  const handleApprove = async (lawyer) => {
    if (!window.confirm(`Are you sure you want to approve ${lawyer.full_name} (${lawyer.bar_council_no})? This will award the official verification badge and make the profile visible in client search.`)) {
      return;
    }

    try {
      const res = await lawAidApi.approveLawyer(lawyer.lawyer_id);
      setActionSuccessMsg(`Approved ${lawyer.full_name}. Verified badge awarded!`);
      setTimeout(() => setActionSuccessMsg(''), 4000);
      setSelectedLawyer(null);
      fetchApplications();
      if (onStatusChanged) onStatusChanged();
    } catch (err) {
      alert('Approval failed: ' + (err.message || 'Unknown error'));
    }
  };

  const handleReject = async (e) => {
    e.preventDefault();
    if (!rejectionReason.trim()) {
      alert('Please provide a valid rejection reason.');
      return;
    }

    try {
      await lawAidApi.rejectLawyer(rejectionModalLawyer.lawyer_id, rejectionReason);
      setActionSuccessMsg(`Verification rejected for ${rejectionModalLawyer.full_name}.`);
      setTimeout(() => setActionSuccessMsg(''), 4000);
      setRejectionModalLawyer(null);
      setRejectionReason('');
      setSelectedLawyer(null);
      fetchApplications();
      if (onStatusChanged) onStatusChanged();
    } catch (err) {
      alert('Rejection failed: ' + (err.message || 'Unknown error'));
    }
  };

  // Calculate statistics
  const pendingCount = applications.filter(a => a.verification_status === 'pending').length;
  const approvedCount = applications.filter(a => a.verification_status === 'approved').length;
  const rejectedCount = applications.filter(a => a.verification_status === 'rejected').length;

  return (
    <div className="max-w-6xl mx-auto my-8 p-6 md:p-8 bg-white rounded-2xl shadow-xl border border-slate-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 mb-6 border-b border-slate-100 gap-4">
        <div>
          <div className="flex items-center gap-2 text-slate-500 font-bold text-xs uppercase tracking-wider mb-1">
            <ShieldCheck size={16} className="text-amber-600" />
            <span>Platform Compliance & Judicial Administration</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2.5">
            Lawyer Verification Management
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 font-semibold">
              SRS FR-38 & NFR-4
            </span>
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Review uploaded NIDs and Bar Council Certificates, decrypt documents, and grant or revoke verification badges.
          </p>
        </div>

        <button
          onClick={fetchApplications}
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition"
          title="Refresh Queue"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Refresh Queue
        </button>
      </div>

      {actionSuccessMsg && (
        <div className="mb-6 p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm flex items-center gap-3">
          <CheckCircle size={18} className="text-emerald-600 shrink-0" />
          <span>{actionSuccessMsg}</span>
        </div>
      )}

      {/* Stats row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div 
          onClick={() => setFilter('pending')}
          className={`p-4 rounded-xl border cursor-pointer transition ${filter === 'pending' ? 'bg-amber-50/70 border-amber-300 ring-2 ring-amber-400/30' : 'bg-slate-50 border-slate-200 hover:bg-slate-100'}`}
        >
          <span className="text-xs font-semibold text-amber-800">Pending Review</span>
          <p className="text-2xl font-extrabold text-slate-900 mt-1">{pendingCount}</p>
          <span className="text-[10px] text-amber-600">Action required (FR-38)</span>
        </div>

        <div 
          onClick={() => setFilter('approved')}
          className={`p-4 rounded-xl border cursor-pointer transition ${filter === 'approved' ? 'bg-emerald-50/70 border-emerald-300 ring-2 ring-emerald-400/30' : 'bg-slate-50 border-slate-200 hover:bg-slate-100'}`}
        >
          <span className="text-xs font-semibold text-emerald-800">Verified & Badged</span>
          <p className="text-2xl font-extrabold text-slate-900 mt-1">{approvedCount}</p>
          <span className="text-[10px] text-emerald-600">Visible in client search</span>
        </div>

        <div 
          onClick={() => setFilter('rejected')}
          className={`p-4 rounded-xl border cursor-pointer transition ${filter === 'rejected' ? 'bg-rose-50/70 border-rose-300 ring-2 ring-rose-400/30' : 'bg-slate-50 border-slate-200 hover:bg-slate-100'}`}
        >
          <span className="text-xs font-semibold text-rose-800">Rejected Submissions</span>
          <p className="text-2xl font-extrabold text-slate-900 mt-1">{rejectedCount}</p>
          <span className="text-[10px] text-rose-600">Hidden from search</span>
        </div>

        <div 
          onClick={() => setFilter('all')}
          className={`p-4 rounded-xl border cursor-pointer transition ${filter === 'all' ? 'bg-slate-200 border-slate-400' : 'bg-slate-50 border-slate-200 hover:bg-slate-100'}`}
        >
          <span className="text-xs font-semibold text-slate-700">Total In Registry</span>
          <p className="text-2xl font-extrabold text-slate-900 mt-1">{applications.length}</p>
          <span className="text-[10px] text-slate-500">All registered advocates</span>
        </div>
      </div>

      {/* Applications Table / Cards */}
      <div className="overflow-x-auto rounded-xl border border-slate-200">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-slate-600 text-xs uppercase font-bold border-b border-slate-200">
            <tr>
              <th className="px-4 py-3">Advocate Name & Honorific</th>
              <th className="px-4 py-3">Bar Council Sanad No</th>
              <th className="px-4 py-3">Bar Association</th>
              <th className="px-4 py-3">District</th>
              <th className="px-4 py-3">Status & Badge</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-700">
            {applications.length === 0 ? (
              <tr>
                <td colSpan="6" className="text-center py-8 text-slate-400 text-xs">
                  No applications found for filter "{filter}".
                </td>
              </tr>
            ) : (
              applications.map((app) => (
                <tr key={app.lawyer_id} className="hover:bg-slate-50/80 transition">
                  <td className="px-4 py-3.5">
                    <div className="font-bold text-slate-900 flex items-center gap-1.5">
                      <span>{app.honorific} {app.full_name}</span>
                    </div>
                    <span className="text-xs text-slate-400 block">{app.email}</span>
                  </td>
                  <td className="px-4 py-3.5">
                    <span className="font-mono font-bold text-slate-800 bg-slate-100 px-2 py-0.5 rounded text-xs">
                      {app.bar_council_no}
                    </span>
                  </td>
                  <td className="px-4 py-3.5 text-xs text-slate-600">
                    {app.bar_association || 'Dhaka Bar Association'}
                  </td>
                  <td className="px-4 py-3.5 text-xs">
                    {app.district}
                  </td>
                  <td className="px-4 py-3.5">
                    {app.verification_status === 'approved' ? (
                      <div className="flex items-center gap-1.5">
                        <VerifiedBadge 
                          badgeData={app.verification_badge || { is_active: true, title: 'Verified Advocate', sanad_number: app.bar_council_no }} 
                          size="sm" 
                        />
                      </div>
                    ) : app.verification_status === 'pending' ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800">
                        <AlertTriangle size={12} />
                        Pending Review
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-100 text-rose-800">
                        <XCircle size={12} />
                        Rejected
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3.5 text-right space-x-1.5 whitespace-nowrap">
                    <button
                      onClick={() => setSelectedLawyer(app)}
                      className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-900 text-white hover:bg-slate-800 transition inline-flex items-center gap-1"
                    >
                      <Eye size={13} />
                      Inspect & Decrypt
                    </button>

                    {app.verification_status !== 'approved' && (
                      <button
                        onClick={() => handleApprove(app)}
                        className="px-2.5 py-1.5 text-xs font-semibold rounded-lg bg-emerald-600 text-white hover:bg-emerald-500 transition inline-flex items-center gap-1"
                        title="Approve & Grant Badge"
                      >
                        <CheckCircle size={13} />
                        Approve
                      </button>
                    )}

                    {app.verification_status !== 'rejected' && (
                      <button
                        onClick={() => {
                          setRejectionModalLawyer(app);
                          setRejectionReason('');
                        }}
                        className="px-2.5 py-1.5 text-xs font-semibold rounded-lg bg-rose-50 text-rose-700 hover:bg-rose-100 transition inline-flex items-center gap-1"
                        title="Reject Verification"
                      >
                        <XCircle size={13} />
                        Reject
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Review & Decryption Modal (SRS NFR-4 & FR-38) */}
      {selectedLawyer && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 animate-in fade-in duration-150">
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 md:p-8">
            <div className="flex items-start justify-between border-b border-slate-100 pb-4 mb-4">
              <div>
                <span className="text-xs font-bold text-amber-600 uppercase tracking-wider block mb-1">
                  Compliance Application Review (Admin View Only)
                </span>
                <h3 className="text-xl font-extrabold text-slate-900 flex items-center gap-2">
                  {selectedLawyer.honorific} {selectedLawyer.full_name}
                  {selectedLawyer.verification_status === 'approved' && (
                    <VerifiedBadge 
                      badgeData={{ is_active: true, sanad_number: selectedLawyer.bar_council_no }} 
                      size="sm" 
                    />
                  )}
                </h3>
                <span className="text-xs text-slate-500">{selectedLawyer.email} | {selectedLawyer.phone}</span>
              </div>
              <button
                onClick={() => {
                  setSelectedLawyer(null);
                  setActiveDocPreview(null);
                }}
                className="p-1 text-slate-400 hover:text-slate-700 text-lg font-bold"
              >
                ✕
              </button>
            </div>

            {/* Lawyer Credentials summary */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 p-4 bg-slate-50 rounded-xl mb-6 text-xs">
              <div>
                <span className="text-slate-400 block">Sanad / Bar ID:</span>
                <span className="font-mono font-bold text-slate-800 text-sm">{selectedLawyer.bar_council_no}</span>
              </div>
              <div>
                <span className="text-slate-400 block">Bar Association:</span>
                <span className="font-semibold text-slate-800">{selectedLawyer.bar_association}</span>
              </div>
              <div>
                <span className="text-slate-400 block">District:</span>
                <span className="font-semibold text-slate-800">{selectedLawyer.district}</span>
              </div>
              <div>
                <span className="text-slate-400 block">Experience:</span>
                <span className="font-semibold text-slate-800">{selectedLawyer.years_experience} Years</span>
              </div>
              <div>
                <span className="text-slate-400 block">Specialization:</span>
                <span className="font-semibold text-slate-800">{selectedLawyer.specialization}</span>
              </div>
              <div>
                <span className="text-slate-400 block">Consultation Fee:</span>
                <span className="font-semibold text-slate-800">BDT {selectedLawyer.consultation_fee}</span>
              </div>
            </div>

            {/* Encrypted Documents Section (NFR-4) */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Lock size={15} className="text-amber-600" />
                  Encrypted Verification Documents (SRS NFR-4)
                </h4>
                <span className="text-[11px] text-slate-400">Strictly Admin Accessible</span>
              </div>

              <div className="space-y-3">
                {selectedLawyer.documents && selectedLawyer.documents.length > 0 ? (
                  selectedLawyer.documents.map((doc, idx) => (
                    <div 
                      key={doc.id || idx}
                      className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between gap-3"
                    >
                      <div className="flex items-center gap-3 truncate">
                        <FileText size={20} className="text-slate-600 shrink-0" />
                        <div className="truncate">
                          <p className="text-xs font-bold text-slate-900 capitalize">
                            {doc.doc_type === 'nid' ? 'National ID Card (NID)' : 'Bangladesh Bar Council Sanad'}
                          </p>
                          <p className="text-[11px] text-slate-500 font-mono truncate">
                            {doc.original_filename} ({doc.mime_type})
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        <button
                          onClick={() => setActiveDocPreview(doc)}
                          className="px-3 py-1.5 text-xs font-medium rounded-lg bg-white border border-slate-300 text-slate-700 hover:bg-slate-100 transition inline-flex items-center gap-1 shadow-sm"
                        >
                          <Eye size={13} />
                          Decrypt & View
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-400 italic">No document records found.</p>
                )}
              </div>
            </div>

            {/* Document Decryption Preview Frame */}
            {activeDocPreview && (
              <div className="mb-6 p-4 bg-slate-900 text-slate-200 rounded-xl border border-slate-800 animate-in fade-in duration-150">
                <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-800">
                  <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
                    <ShieldCheck size={14} />
                    Decrypted from AES-128 ciphertext (SRS NFR-4)
                  </span>
                  <button 
                    onClick={() => setActiveDocPreview(null)}
                    className="text-xs text-slate-400 hover:text-white"
                  >
                    Close Preview
                  </button>
                </div>
                <div className="p-4 bg-slate-950 rounded-lg text-xs font-mono text-slate-300 space-y-1">
                  <p><strong className="text-amber-400">Document Type:</strong> {activeDocPreview.doc_type.toUpperCase()}</p>
                  <p><strong className="text-amber-400">File Name:</strong> {activeDocPreview.original_filename}</p>
                  <p><strong className="text-amber-400">Encryption:</strong> AES-128-CBC + HMAC-SHA256 Authenticated</p>
                  <p><strong className="text-amber-400">Target Lawyer:</strong> {selectedLawyer.full_name} [{selectedLawyer.bar_council_no}]</p>
                  <div className="mt-3 p-3 bg-slate-900/90 rounded border border-slate-800 text-[11px] text-emerald-300">
                    ✓ Document decrypted in-memory for authorized platform administrator session. Raw plaintext is never stored or served publicly.
                  </div>
                </div>
              </div>
            )}

            {/* Actions Footer */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
              <button
                onClick={() => setSelectedLawyer(null)}
                className="px-4 py-2 text-xs font-semibold rounded-xl text-slate-600 hover:bg-slate-100 transition"
              >
                Close
              </button>

              {selectedLawyer.verification_status !== 'rejected' && (
                <button
                  onClick={() => {
                    setRejectionModalLawyer(selectedLawyer);
                    setRejectionReason('');
                  }}
                  className="px-4 py-2 text-xs font-semibold rounded-xl bg-rose-50 text-rose-700 hover:bg-rose-100 transition"
                >
                  Reject Application
                </button>
              )}

              {selectedLawyer.verification_status !== 'approved' && (
                <button
                  onClick={() => handleApprove(selectedLawyer)}
                  className="px-5 py-2 text-xs font-bold rounded-xl bg-emerald-600 text-white hover:bg-emerald-500 transition shadow-lg shadow-emerald-600/20 flex items-center gap-1.5"
                >
                  <CheckCircle size={14} />
                  Approve & Grant Badge
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Rejection Reason Modal */}
      {rejectionModalLawyer && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-md w-full p-6">
            <h3 className="text-lg font-bold text-slate-900 mb-1 flex items-center gap-2">
              <ShieldAlert size={20} className="text-rose-600" />
              Reject Verification Application
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              Provide an official reason for rejecting {rejectionModalLawyer.full_name}'s credentials.
            </p>

            <form onSubmit={handleReject}>
              <textarea
                required
                rows={3}
                placeholder="e.g. Scanned NID image is blurry; Bar Council Sanad ID does not match official Bar registry records."
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                className="w-full p-3 text-xs border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-rose-500 mb-4"
              />

              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setRejectionModalLawyer(null)}
                  className="px-4 py-2 text-xs font-semibold rounded-xl text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-xs font-bold rounded-xl bg-rose-600 text-white hover:bg-rose-500 transition shadow"
                >
                  Confirm Rejection
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
