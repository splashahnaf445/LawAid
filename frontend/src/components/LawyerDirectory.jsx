import React, { useState, useEffect } from 'react';
import { 
  Search, 
  MapPin, 
  Award, 
  Briefcase, 
  Star, 
  Calendar, 
  MessageSquare, 
  Filter, 
  ShieldCheck, 
  AlertCircle,
  Eye,
  SlidersHorizontal
} from 'lucide-react';
import { lawAidApi } from '../services/api';
import VerifiedBadge from './VerifiedBadge';

export default function LawyerDirectory({ onSelectLawyer }) {
  const [lawyers, setLawyers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [districtFilter, setDistrictFilter] = useState('');
  const [debugShowAll, setDebugShowAll] = useState(false); // Toggle to inspect verified-only enforcement

  const fetchLawyers = async () => {
    setLoading(true);
    try {
      const params = {};
      if (searchTerm) params.q = searchTerm;
      if (districtFilter) params.district = districtFilter;
      if (debugShowAll) params.all = true;

      const res = await lawAidApi.searchLawyers(params);
      setLawyers(res.results || []);
    } catch (err) {
      console.error('Error fetching lawyers:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLawyers();
  }, [searchTerm, districtFilter, debugShowAll]);

  return (
    <div className="max-w-6xl mx-auto my-8 p-6 md:p-8 bg-white rounded-2xl shadow-xl border border-slate-200">
      {/* Directory Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 mb-6 border-b border-slate-100 gap-4">
        <div>
          <div className="flex items-center gap-2 text-emerald-600 font-bold text-xs uppercase tracking-wider mb-1">
            <ShieldCheck size={16} />
            <span>Verified Legal Practitioner Network</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight">
            Find Verified Advocates
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Browse genuine Bangladesh Bar Council certified lawyers. Unverified lawyers are hidden from public search (SRS FR-3).
          </p>
        </div>

        {/* View Mode Switcher to demonstrate FR-3 */}
        <div className="p-2 bg-slate-100 rounded-xl flex items-center gap-2 border border-slate-200 self-start md:self-auto text-xs">
          <span className="text-slate-500 font-medium pl-1">Perspective:</span>
          <button
            onClick={() => setDebugShowAll(false)}
            className={`px-3 py-1 rounded-lg font-semibold transition ${!debugShowAll ? 'bg-white shadow text-slate-900' : 'text-slate-600 hover:text-slate-900'}`}
          >
            Public Client View (Verified Only)
          </button>
          <button
            onClick={() => setDebugShowAll(true)}
            className={`px-3 py-1 rounded-lg font-semibold transition ${debugShowAll ? 'bg-amber-500 text-white shadow' : 'text-slate-600 hover:text-slate-900'}`}
          >
            Inspector Mode (Show All)
          </button>
        </div>
      </div>

      {/* SRS Compliance Alert Banner */}
      <div className="mb-6 p-4 rounded-xl bg-emerald-50/70 border border-emerald-200 text-emerald-900 text-xs flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Award size={18} className="text-emerald-600 shrink-0" />
          <span>
            <strong>SRS FR-3 Strict Enforcement:</strong> Only advocates who have completed NID and Bar Council Sanad verification by an administrator appear in client search and carry the official verified badge.
          </span>
        </div>
        <span className="px-2 py-0.5 rounded bg-emerald-200/80 text-emerald-900 font-bold text-[10px] shrink-0">
          FR-3 Active
        </span>
      </div>

      {/* Search & Filter Toolbar */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-8">
        <div className="relative md:col-span-2">
          <Search size={16} className="absolute left-3.5 top-3.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search by advocate name, specialization (e.g. Civil, Criminal, Writ), or Bar ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500"
          />
        </div>

        <div>
          <select
            value={districtFilter}
            onChange={(e) => setDistrictFilter(e.target.value)}
            className="w-full px-3.5 py-2.5 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500 text-slate-700"
          >
            <option value="">All Districts</option>
            <option value="Dhaka">Dhaka</option>
            <option value="Chittagong">Chittagong</option>
            <option value="Sylhet">Sylhet</option>
            <option value="Rajshahi">Rajshahi</option>
          </select>
        </div>
      </div>

      {/* Lawyers Grid */}
      {loading ? (
        <div className="py-16 text-center text-slate-400 text-sm">
          <span className="animate-spin inline-block rounded-full h-6 w-6 border-2 border-slate-400 border-t-transparent mb-2"></span>
          <p>Loading verified advocates from registry...</p>
        </div>
      ) : lawyers.length === 0 ? (
        <div className="py-16 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-300">
          <AlertCircle size={36} className="mx-auto text-slate-400 mb-2" />
          <h3 className="text-base font-bold text-slate-700">No verified lawyers found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
            {debugShowAll 
              ? "No lawyers match your current search query." 
              : "Lawyers currently pending admin verification are hidden from client search per SRS FR-3."}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {lawyers.map((lawyer) => {
            const isApproved = lawyer.verification_status === 'approved';

            return (
              <div 
                key={lawyer.lawyer_id}
                className={`p-5 rounded-2xl border transition-all duration-200 flex flex-col justify-between ${
                  isApproved 
                    ? 'bg-white border-slate-200 hover:border-slate-400 shadow-sm hover:shadow-md' 
                    : 'bg-amber-50/30 border-dashed border-amber-300 opacity-80'
                }`}
              >
                <div>
                  {/* Top card bar */}
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <h3 className="text-lg font-bold text-slate-900">
                          {lawyer.honorific} {lawyer.full_name}
                        </h3>
                        {/* SRS FR-3 Verification Badge */}
                        <VerifiedBadge 
                          badgeData={lawyer.verification_badge || (isApproved ? { is_active: true, sanad_number: lawyer.bar_council_no } : null)}
                          size="sm"
                        />
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5">{lawyer.headline}</p>
                    </div>

                    <span className="font-bold text-slate-900 text-sm shrink-0">
                      ৳{lawyer.consultation_fee}
                      <span className="text-[10px] text-slate-400 font-normal block text-right">/ session</span>
                    </span>
                  </div>

                  {/* Badges & Meta */}
                  <div className="flex flex-wrap items-center gap-2 mb-3 text-xs">
                    <span className="inline-flex items-center gap-1 font-mono font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                      Sanad: {lawyer.bar_council_no}
                    </span>
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                      <MapPin size={12} className="text-slate-400" />
                      {lawyer.district}
                    </span>
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                      <Briefcase size={12} className="text-slate-400" />
                      {lawyer.years_experience} yrs exp.
                    </span>
                    {Number(lawyer.avg_rating) > 0 && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-amber-50 text-amber-800 font-bold">
                        <Star size={12} className="fill-amber-400 text-amber-400" />
                        {lawyer.avg_rating} ({lawyer.review_count})
                      </span>
                    )}
                  </div>

                  {/* Specialization */}
                  <p className="text-xs text-slate-600 line-clamp-2 mb-4">
                    <strong className="text-slate-800">Specialization:</strong> {lawyer.specialization}
                  </p>

                  {!isApproved && (
                    <div className="p-2 mb-4 rounded-lg bg-amber-100/70 text-amber-800 text-[11px] font-medium flex items-center gap-1.5">
                      <AlertCircle size={14} className="shrink-0" />
                      <span>Notice: This lawyer is currently <strong>Pending Admin Review</strong> and is only visible because Inspector Mode is enabled.</span>
                    </div>
                  )}
                </div>

                {/* Card Actions */}
                <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-xs text-slate-400 font-medium">
                    {lawyer.bar_association}
                  </span>
                  <button
                    onClick={() => onSelectLawyer && onSelectLawyer(lawyer)}
                    className="px-4 py-2 rounded-xl bg-slate-900 text-white font-semibold text-xs hover:bg-slate-800 transition flex items-center gap-1.5 cursor-pointer shadow-sm"
                  >
                    <Eye size={13} />
                    View Profile & Badge
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
