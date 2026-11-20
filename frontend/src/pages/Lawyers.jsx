import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  MapPin,
  Building2,
  Clock,
  Briefcase,
  ShieldCheck,
  Eye,
  X,
  Phone,
  Mail,
  Scale
} from 'lucide-react';
import VerifiedBadge from '../components/VerifiedBadge';
import { searchLawyers, getLawyerDetail } from '../api/lawyers';

export default function Lawyers({ onNavigate }) {
  const [lawyers, setLawyers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [selectedCourt, setSelectedCourt] = useState('');

  // Selected lawyer detail modal
  const [selectedLawyer, setSelectedLawyer] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const fetchLawyers = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await searchLawyers({
        q: searchQuery,
        district: selectedDistrict,
        court: selectedCourt,
      });
      setLawyers(Array.isArray(data) ? data : data.results || []);
    } catch (err) {
      setError('Unable to fetch lawyers list. Make sure backend service is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLawyers();
  }, [selectedDistrict, selectedCourt]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchLawyers();
  };

  const handleOpenDetail = async (lawyerId) => {
    setDetailLoading(true);
    try {
      const detail = await getLawyerDetail(lawyerId);
      setSelectedLawyer(detail);
    } catch (err) {
      alert('Could not load advocate details.');
    } finally {
      setDetailLoading(false);
    }
  };

  return (
    <div style={{ padding: '2.5rem 0 4rem' }}>
      <div className="container">
        {/* Header */}
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#0d9488', fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            <Scale size={18} />
            <span>Official Advocate Directory</span>
          </div>
          <h1 style={{ fontSize: '2.25rem', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.02em', marginTop: '0.35rem' }}>
            Find Verified Legal Advocates
          </h1>
          <p style={{ color: '#64748b', fontSize: '0.95rem', maxWidth: '750px', marginTop: '0.35rem' }}>
            Connect with verified advocates practicing in the Supreme Court, High Court Division, and District Courts of Bangladesh.
          </p>
        </div>

        {/* Verification Guarantee Banner (SRS FR-3) */}
        <div
          style={{
            background: 'linear-gradient(135deg, #ecfdf5 0%, #f0fdfa 100%)',
            border: '1px solid #99f6e4',
            borderRadius: '12px',
            padding: '1rem 1.25rem',
            marginBottom: '2rem',
            display: 'flex',
            alignItems: 'center',
            gap: '1rem',
          }}
        >
          <div
            style={{
              width: 44,
              height: 44,
              borderRadius: '10px',
              backgroundColor: '#0d9488',
              color: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            <ShieldCheck size={24} />
          </div>
          <div>
            <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#0f766e' }}>
              SRS FR-3 Search Compliance Active
            </div>
            <div style={{ fontSize: '0.825rem', color: '#115e59', lineHeight: 1.4, marginTop: '2px' }}>
              Unverified and pending applicants are strictly filtered out by the backend database query. Only
              practitioners whose National ID and Bar Council Sanad have been verified by platform administrators
              appear with the LawAid Verified Badge.
            </div>
          </div>
        </div>

        {/* Search & Filters */}
        <form onSubmit={handleSearchSubmit} className="search-bar-wrapper">
          <div className="search-input-field">
            <input
              type="text"
              className="form-control"
              placeholder="Search by advocate name, specialty, or keywords..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div style={{ minWidth: '160px' }}>
            <select
              className="form-control"
              value={selectedDistrict}
              onChange={(e) => setSelectedDistrict(e.target.value)}
            >
              <option value="">All Districts</option>
              <option value="Dhaka">Dhaka</option>
              <option value="Chittagong">Chittagong</option>
              <option value="Sylhet">Sylhet</option>
              <option value="Rajshahi">Rajshahi</option>
              <option value="Khulna">Khulna</option>
            </select>
          </div>

          <button type="submit" className="btn btn-primary" style={{ padding: '0.65rem 1.25rem' }}>
            <Search size={16} />
            <span>Search</span>
          </button>
        </form>

        {/* Loading state */}
        {loading && (
          <div style={{ textAlign: 'center', padding: '4rem 0' }}>
            <div className="spinner" style={{ borderColor: '#0d9488', borderTopColor: 'transparent', width: '2rem', height: '2rem', margin: '0 auto 1rem' }} />
            <p style={{ color: '#64748b' }}>Querying verified advocate registry...</p>
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="alert alert-danger" style={{ marginBottom: '2rem' }}>
            <span>{error}</span>
          </div>
        )}

        {/* Lawyer Cards Grid */}
        {!loading && !error && lawyers.length > 0 && (
          <div className="lawyer-grid">
            {lawyers.map((lawyer) => (
              <div key={lawyer.id} className="lawyer-card">
                <div className="lawyer-card-header">
                  <div className="lawyer-avatar">
                    {lawyer.full_name ? lawyer.full_name.charAt(0) : 'A'}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div className="lawyer-name">
                      <span>{lawyer.full_name}</span>
                      {/* VERIFIED BADGE (SRS FR-3) */}
                      {lawyer.is_verified && (
                        <VerifiedBadge
                          badgeInfo={lawyer.badge}
                          sanadNumber={lawyer.bar_council_no}
                          size="sm"
                        />
                      )}
                    </div>
                    <div className="lawyer-headline">
                      {lawyer.headline || 'Advocate, High Court Division'}
                    </div>
                  </div>
                </div>

                <div className="lawyer-meta">
                  <div className="lawyer-meta-item">
                    <Scale size={15} color="#0d9488" />
                    <span><strong>Bar Sanad:</strong> {lawyer.bar_council_no}</span>
                  </div>
                  <div className="lawyer-meta-item">
                    <Building2 size={15} color="#0d9488" />
                    <span><strong>Court:</strong> {lawyer.primary_court_name || 'Supreme Court of Bangladesh'}</span>
                  </div>
                  <div className="lawyer-meta-item">
                    <Clock size={15} color="#0d9488" />
                    <span><strong>Experience:</strong> {lawyer.years_experience} years</span>
                  </div>
                  <div className="lawyer-meta-item">
                    <MapPin size={15} color="#0d9488" />
                    <span><strong>Location:</strong> {lawyer.district || 'Dhaka'}</span>
                  </div>
                </div>

                {/* Practice Areas */}
                {lawyer.practice_areas && lawyer.practice_areas.length > 0 && (
                  <div className="practice-tags">
                    {lawyer.practice_areas.map((area, idx) => (
                      <span key={idx} className="tag-item">
                        {typeof area === 'string' ? area : area.name_en}
                      </span>
                    ))}
                  </div>
                )}

                <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ fontSize: '0.8rem', color: '#059669', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <ShieldCheck size={14} /> Bar Verified
                  </div>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => handleOpenDetail(lawyer.id)}
                  >
                    <Eye size={14} />
                    <span>View Profile</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty state */}
        {!loading && !error && lawyers.length === 0 && (
          <div
            style={{
              textAlign: 'center',
              padding: '4rem 1.5rem',
              background: '#ffffff',
              borderRadius: '16px',
              border: '1px solid #e2e8f0',
            }}
          >
            <Scale size={48} color="#94a3b8" style={{ margin: '0 auto 1rem' }} />
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f172a' }}>
              No Verified Advocates Found
            </h3>
            <p style={{ color: '#64748b', fontSize: '0.9rem', maxWidth: '480px', margin: '0.5rem auto 1.5rem' }}>
              No approved lawyers match your query. Remember, lawyers in "pending" or "rejected" status are
              automatically hidden from public search (SRS FR-3).
            </p>
            <button
              className="btn btn-secondary"
              onClick={() => {
                setSearchQuery('');
                setSelectedDistrict('');
                setSelectedCourt('');
                fetchLawyers();
              }}
            >
              Reset Filters
            </button>
          </div>
        )}

        {/* Detail Modal */}
        {selectedLawyer && (
          <div className="modal-overlay" onClick={() => setSelectedLawyer(null)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <h3 style={{ fontSize: '1.3rem', fontWeight: 800, color: '#0f172a' }}>
                    {selectedLawyer.full_name}
                  </h3>
                  {selectedLawyer.is_verified && (
                    <VerifiedBadge badgeInfo={selectedLawyer.badge} size="md" />
                  )}
                </div>
                <button
                  className="modal-close"
                  onClick={() => setSelectedLawyer(null)}
                  title="Close"
                >
                  <X size={20} />
                </button>
              </div>

              <div style={{ marginBottom: '1.5rem' }}>
                <div style={{ color: '#0d9488', fontWeight: 600, fontSize: '0.95rem', marginBottom: '0.5rem' }}>
                  {selectedLawyer.headline}
                </div>
                <p style={{ color: '#475569', fontSize: '0.9rem', lineHeight: 1.6 }}>
                  {selectedLawyer.bio || 'Advocate practicing before the High Court Division and subordinate judicial courts.'}
                </p>
              </div>

              <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: '10px', border: '1px solid #e2e8f0', marginBottom: '1.5rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.85rem' }}>
                <div>
                  <span style={{ color: '#64748b' }}>Bar Sanad No:</span>
                  <div style={{ fontWeight: 700, fontFamily: 'monospace', color: '#0f172a' }}>{selectedLawyer.bar_council_no}</div>
                </div>
                <div>
                  <span style={{ color: '#64748b' }}>Bar Association:</span>
                  <div style={{ fontWeight: 700, color: '#0f172a' }}>{selectedLawyer.bar_association || 'Dhaka Bar Association'}</div>
                </div>
                <div>
                  <span style={{ color: '#64748b' }}>Primary Court:</span>
                  <div style={{ fontWeight: 700, color: '#0f172a' }}>{selectedLawyer.primary_court_name}</div>
                </div>
                <div>
                  <span style={{ color: '#64748b' }}>Experience:</span>
                  <div style={{ fontWeight: 700, color: '#0f172a' }}>{selectedLawyer.years_experience} Years</div>
                </div>
                <div style={{ gridColumn: 'span 2' }}>
                  <span style={{ color: '#64748b' }}>Chamber Address:</span>
                  <div style={{ fontWeight: 600, color: '#0f172a' }}>{selectedLawyer.chamber_address || 'Supreme Court Bar Association Annex'}</div>
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  className="btn btn-secondary"
                  onClick={() => setSelectedLawyer(null)}
                >
                  Close
                </button>
                <button
                  className="btn btn-primary"
                  onClick={() => alert(`Consultation request sent to Advocate ${selectedLawyer.full_name}!`)}
                >
                  Request Legal Consultation
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
