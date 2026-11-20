import React from 'react';
import { User, Scale, ArrowRight, ShieldCheck } from 'lucide-react';
import AuthShell from '../components/AuthShell';

export default function RoleSelect({ onSelectRole, onNavigate }) {
  return (
    <AuthShell
      title="Join LawAid"
      subtitle="Select the type of account you want to create"
      wide
    >
      <div className="role-grid">
        {/* Client Card */}
        <div
          className="role-card"
          onClick={() => onSelectRole('client')}
        >
          <div className="role-icon">
            <User size={32} />
          </div>
          <h3 className="role-title">Client Account</h3>
          <p className="role-desc">
            Find verified advocates, book legal consultations, request pro-bono aid, and manage active cases securely.
          </p>
          <div style={{ marginTop: '1.5rem', width: '100%' }}>
            <button className="btn btn-secondary" style={{ width: '100%' }}>
              <span>Continue as Client</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </div>

        {/* Lawyer Card */}
        <div
          className="role-card"
          onClick={() => onSelectRole('lawyer')}
          style={{ borderColor: '#99f6e4' }}
        >
          <div className="role-icon" style={{ backgroundColor: '#f0fdfa', color: '#0f766e' }}>
            <Scale size={32} />
          </div>
          <h3 className="role-title" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span>Lawyer / Advocate</span>
            <ShieldCheck size={18} color="#059669" />
          </h3>
          <p className="role-desc">
            Enrolled advocate in Bangladesh Bar Council. Requires NID and Sanad certificate verification for public badge.
          </p>
          <div style={{ marginTop: '1.5rem', width: '100%' }}>
            <button className="btn btn-primary" style={{ width: '100%' }}>
              <span>Register with Bar Sanad</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </div>

      <div style={{ textAlign: 'center', marginTop: '2rem', fontSize: '0.9rem', color: '#64748b' }}>
        Already have an account?{' '}
        <a
          href="#login"
          onClick={(e) => {
            e.preventDefault();
            onNavigate('login');
          }}
          style={{ fontWeight: 600 }}
        >
          Sign In
        </a>
      </div>
    </AuthShell>
  );
}
