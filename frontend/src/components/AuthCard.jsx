import React from 'react';

// Ahnaf (SYS-21/22): the light auth card used by his Login page. Kept from
// feature/lawyer-verification-and-badge as AuthCard because AuthShell.jsx is Usama's component
// (different props) used by the registration pages.
import { Scale, ShieldCheck, Lock } from 'lucide-react';

export default function AuthCard({
  title,
  subtitle,
  children,
  wide = false,
  badgeIcon: BadgeIcon = Scale,
}) {
  return (
    <div className="auth-wrapper">
      <div className={`auth-card ${wide ? 'auth-card-wide' : ''}`}>
        <div className="auth-header">
          <div className="logo-badge">
            <BadgeIcon size={28} />
          </div>
          <h2 className="auth-title">{title}</h2>
          {subtitle && <p className="auth-subtitle">{subtitle}</p>}
        </div>

        {children}

        <div
          style={{
            marginTop: '2rem',
            paddingTop: '1.25rem',
            borderTop: '1px solid #e2e8f0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '1.5rem',
            fontSize: '0.75rem',
            color: '#64748b',
          }}
        >
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <ShieldCheck size={14} color="#0d9488" /> Verified Advocates Only
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Lock size={14} color="#0d9488" /> 256-bit Encrypted Storage
          </span>
        </div>
      </div>
    </div>
  );
}
