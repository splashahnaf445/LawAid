import React from 'react';
import { 
  ShieldCheck, 
  MapPin, 
  Briefcase, 
  Award, 
  Star, 
  Clock, 
  Calendar, 
  Phone, 
  Mail, 
  AlertTriangle,
  CheckCircle2,
  Lock
} from 'lucide-react';
import VerifiedBadge from './VerifiedBadge';

export default function LawyerProfileModal({ lawyer, onClose }) {
  if (!lawyer) return null;

  const isApproved = lawyer.verification_status === 'approved';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 animate-in fade-in duration-150">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 md:p-8">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-slate-100 pb-5 mb-5">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-slate-900 text-amber-400 flex items-center justify-center text-xl font-bold font-mono shadow-md">
              {lawyer.full_name?.split(' ').map(n => n[0]).join('').slice(0, 2) || 'AD'}
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h2 className="text-xl md:text-2xl font-black text-slate-900 tracking-tight">
                  {lawyer.honorific} {lawyer.full_name}
                </h2>
                {/* SRS FR-3 Verified Badge */}
                <VerifiedBadge 
                  badgeData={lawyer.verification_badge || (isApproved ? { is_active: true, sanad_number: lawyer.bar_council_no } : null)}
                  size="md"
                />
              </div>
              <p className="text-xs text-slate-500 mt-0.5">{lawyer.headline}</p>
              <p className="text-xs text-slate-400">{lawyer.bar_association}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-700 text-lg font-bold rounded-lg hover:bg-slate-100 transition"
          >
            ✕
          </button>
        </div>

        {/* Verification Status Banner */}
        {isApproved ? (
          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-900 mb-6 flex items-start gap-3">
            <ShieldCheck size={20} className="text-emerald-600 shrink-0 mt-0.5" />
            <div>
              <strong className="block text-emerald-950 font-bold mb-0.5">
                Verified Legal Practitioner (SRS FR-3 Authenticated)
              </strong>
              <span>
                National Identity and Bangladesh Bar Council Sanad ({lawyer.bar_council_no}) verified by LawAid Judicial Compliance. Profile is fully active and visible in public search.
              </span>
            </div>
          </div>
        ) : (
          <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 mb-6 flex items-start gap-3">
            <AlertTriangle size={20} className="text-amber-600 shrink-0 mt-0.5" />
            <div>
              <strong className="block text-amber-950 font-bold mb-0.5">
                Pending Administrator Verification
              </strong>
              <span>
                This advocate's credentials and encrypted documents are in the review queue. In accordance with SRS FR-3, unapproved lawyers remain hidden from public search until officially cleared.
              </span>
            </div>
          </div>
        )}

        {/* Details Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6 p-4 bg-slate-50 rounded-xl text-xs">
          <div>
            <span className="text-slate-400 block mb-0.5">Sanad Number</span>
            <span className="font-mono font-bold text-slate-800 text-sm">{lawyer.bar_council_no}</span>
          </div>
          <div>
            <span className="text-slate-400 block mb-0.5">District</span>
            <span className="font-semibold text-slate-800 flex items-center gap-1">
              <MapPin size={12} className="text-slate-400" />
              {lawyer.district}
            </span>
          </div>
          <div>
            <span className="text-slate-400 block mb-0.5">Experience</span>
            <span className="font-semibold text-slate-800 flex items-center gap-1">
              <Briefcase size={12} className="text-slate-400" />
              {lawyer.years_experience} Years
            </span>
          </div>
          <div>
            <span className="text-slate-400 block mb-0.5">Consultation Fee</span>
            <span className="font-bold text-slate-900 text-sm">৳{lawyer.consultation_fee}</span>
          </div>
        </div>

        {/* Specialization & Bio */}
        <div className="space-y-4 mb-6 text-xs text-slate-700">
          <div>
            <h4 className="font-bold text-slate-900 mb-1">Areas of Practice & Specialization:</h4>
            <p className="bg-slate-50 p-3 rounded-lg border border-slate-200 font-medium">
              {lawyer.specialization}
            </p>
          </div>

          <div>
            <h4 className="font-bold text-slate-900 mb-1">Professional Bio:</h4>
            <p className="text-slate-600 leading-relaxed">
              {lawyer.bio || "Practicing advocate enrolled under Bangladesh Bar Council, available for legal consultations, case management, and court representation."}
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
          <span className="text-xs text-slate-400 flex items-center gap-1.5">
            <Lock size={12} />
            LawAid Verified Trust Framework
          </span>
          <button
            onClick={onClose}
            className="px-5 py-2 text-xs font-bold rounded-xl bg-slate-900 text-white hover:bg-slate-800 transition shadow"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
