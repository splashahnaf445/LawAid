import React from 'react';
import { ShieldCheck, Lock, Search, FileCheck, Scale, ArrowRight, UserCheck, ShieldAlert } from 'lucide-react';

export default function Landing({ onNavigate }) {
  return (
    <div>
      {/* Hero */}
      <section className="hero-section">
        <div className="container">
          <div className="hero-pill">
            <ShieldCheck size={16} color="#059669" />
            <span>Zero-Trust Lawyer Verification System</span>
          </div>

          <h1 className="hero-title">
            Legal Aid You Can Trust with <span className="highlight">Verified Bar Advocates</span>
          </h1>

          <p className="hero-subtitle">
            LawAid protects citizens from fraudulent practitioners. Every advocate is verified against
            official Bangladesh Bar Council records before being visible in public search.
          </p>

          <div className="hero-cta">
            <button
              className="btn btn-primary"
              onClick={() => onNavigate('lawyers')}
              style={{ padding: '0.8rem 1.75rem', fontSize: '1rem' }}
            >
              <Search size={18} />
              <span>Find Verified Advocates</span>
            </button>

            <button
              className="btn btn-secondary"
              onClick={() => onNavigate('register-lawyer')}
              style={{ padding: '0.8rem 1.75rem', fontSize: '1rem' }}
            >
              <Scale size={18} />
              <span>Join as an Advocate</span>
            </button>
          </div>
        </div>
      </section>

      {/* Verification Pipeline Architecture (SRS FR-2, FR-3, NFR-4) */}
      <section style={{ padding: '4rem 0', background: '#ffffff', borderBottom: '1px solid #e2e8f0' }}>
        <div className="container">
          <div style={{ textAlign: 'center', maxWidth: '700px', margin: '0 auto 3rem' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#0d9488', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Trust & Compliance Framework
            </span>
            <h2 style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a', marginTop: '0.4rem' }}>
              How Lawyer Verification Works
            </h2>
            <p style={{ color: '#64748b', fontSize: '0.95rem', marginTop: '0.5rem' }}>
              Strict compliance controls ensure that only authenticated practitioners receive the LawAid badge.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.5rem' }}>
            {/* Step 1 */}
            <div className="card" style={{ textAlign: 'center', position: 'relative' }}>
              <div
                style={{
                  width: 52,
                  height: 52,
                  borderRadius: 14,
                  backgroundColor: '#f0fdfa',
                  color: '#0d9488',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 1.25rem',
                  border: '1px solid #ccfbf1',
                }}
              >
                <FileCheck size={26} />
              </div>
              <span className="badge badge-info" style={{ marginBottom: '0.75rem' }}>Step 1: Ingestion</span>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>
                Document Submission
              </h3>
              <p style={{ fontSize: '0.875rem', color: '#64748b', lineHeight: 1.5 }}>
                Lawyers upload National ID Card & Bangladesh Bar Council Sanad certificate during registration (FR-2).
              </p>
            </div>

            {/* Step 2 */}
            <div className="card" style={{ textAlign: 'center', position: 'relative' }}>
              <div
                style={{
                  width: 52,
                  height: 52,
                  borderRadius: 14,
                  backgroundColor: '#ecfdf5',
                  color: '#059669',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 1.25rem',
                  border: '1px solid #a7f3d0',
                }}
              >
                <Lock size={26} />
              </div>
              <span className="badge badge-success" style={{ marginBottom: '0.75rem' }}>Step 2: Security (NFR-4)</span>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>
                AES Encryption at Rest
              </h3>
              <p style={{ fontSize: '0.875rem', color: '#64748b', lineHeight: 1.5 }}>
                All sensitive files are immediately encrypted with Fernet AES-128-CBC + HMAC-SHA256. Visible ONLY to admins.
              </p>
            </div>

            {/* Step 3 */}
            <div className="card" style={{ textAlign: 'center', position: 'relative' }}>
              <div
                style={{
                  width: 52,
                  height: 52,
                  borderRadius: 14,
                  backgroundColor: '#fffbeb',
                  color: '#d97706',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 1.25rem',
                  border: '1px solid #fde68a',
                }}
              >
                <ShieldAlert size={26} />
              </div>
              <span className="badge badge-warning" style={{ marginBottom: '0.75rem' }}>Step 3: Verification (FR-38)</span>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>
                Admin Compliance Audit
              </h3>
              <p style={{ fontSize: '0.875rem', color: '#64748b', lineHeight: 1.5 }}>
                Platform compliance officers verify Bar Council records and decrypt documents in memory.
              </p>
            </div>

            {/* Step 4 */}
            <div className="card" style={{ textAlign: 'center', position: 'relative' }}>
              <div
                style={{
                  width: 52,
                  height: 52,
                  borderRadius: 14,
                  backgroundColor: '#f0fdf4',
                  color: '#15803d',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 1.25rem',
                  border: '1px solid #bbf7d0',
                }}
              >
                <ShieldCheck size={26} />
              </div>
              <span className="badge badge-success" style={{ marginBottom: '0.75rem' }}>Step 4: Activation (FR-3)</span>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>
                Badge Award & Public Search
              </h3>
              <p style={{ fontSize: '0.875rem', color: '#64748b', lineHeight: 1.5 }}>
                Only upon admin approval is the verified badge displayed, and the profile unlocked for public search.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Compliance Callout Banner */}
      <section style={{ padding: '3.5rem 0', background: '#0f172a', color: '#ffffff' }}>
        <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '2rem' }}>
          <div style={{ maxWidth: '640px' }}>
            <h3 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '0.75rem', color: '#ffffff' }}>
              Are you a licensed Advocate in Bangladesh?
            </h3>
            <p style={{ color: '#94a3b8', fontSize: '0.95rem', lineHeight: 1.6 }}>
              Join LawAid to provide trusted legal consultation and represent clients across District and High Court Divisions.
              Upload your Sanad certificate to get verified today.
            </p>
          </div>
          <div>
            <button
              className="btn btn-primary"
              onClick={() => onNavigate('register-lawyer')}
              style={{ padding: '0.85rem 1.75rem', fontSize: '1rem', backgroundColor: '#0d9488' }}
            >
              <span>Submit Verification Documents</span>
              <ArrowRight size={18} />
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
