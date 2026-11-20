import React from 'react';
import { ShieldCheck } from 'lucide-react';

/**
 * LawAid Official Verification Badge (SRS FR-3, FR-38)
 * Displayed exclusively when verification_status === 'approved'.
 */
export default function VerifiedBadge({
  badgeInfo = null,
  sanadNumber = '',
  verifiedAt = null,
  size = 'md',
  showDetails = true,
  className = ''
}) {
  const sanad = (badgeInfo && badgeInfo.sanad_number) || sanadNumber;
  const date = (badgeInfo && badgeInfo.verified_at) || verifiedAt;
  const label = (badgeInfo && badgeInfo.badge_label) || 'Verified Advocate';

  const iconSizes = {
    sm: 13,
    md: 15,
    lg: 18,
  };

  return (
    <span
      className={`verified-badge size-${size} ${className}`}
      title={sanad ? `Verified by LawAid — Bar Council Sanad: ${sanad}` : 'LawAid Verified Advocate'}
      role="status"
      aria-label="Verified Advocate Badge"
    >
      <ShieldCheck
        size={iconSizes[size] || 15}
        className="verified-badge-icon"
        strokeWidth={2.5}
      />
      <span>{label}</span>

      {showDetails && (
        <span className="verified-tooltip">
          <div style={{ fontWeight: 700, color: '#34d399', marginBottom: '2px' }}>
            Bangladesh Bar Council Verified
          </div>
          {sanad && (
            <div style={{ color: '#e2e8f0', fontSize: '0.72rem' }}>
              Sanad No: <span style={{ fontFamily: 'monospace' }}>{sanad}</span>
            </div>
          )}
          {date && (
            <div style={{ color: '#94a3b8', fontSize: '0.7rem', marginTop: '2px' }}>
              Approved: {new Date(date).toLocaleDateString('en-GB')}
            </div>
          )}
          <div style={{ color: '#94a3b8', fontSize: '0.68rem', marginTop: '4px', borderTop: '1px solid #334155', paddingTop: '3px' }}>
            Identity & documents authenticated (SRS FR-3)
          </div>
        </span>
      )}
    </span>
  );
}
