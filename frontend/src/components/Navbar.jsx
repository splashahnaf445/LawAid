import React from 'react';
import { Scale, ShieldCheck, Users, ClipboardCheck, LogOut, LogIn, UserPlus } from 'lucide-react';
import VerifiedBadge from './VerifiedBadge';

export default function Navbar({
  currentUser,
  activeTab,
  onNavigate,
  onLogout,
}) {
  const isAdmin = currentUser && (currentUser.role === 'admin' || currentUser.is_admin);
  const isLawyer = currentUser && currentUser.role === 'lawyer';

  return (
    <header className="navbar">
      <div className="container navbar-inner">
        {/* Brand */}
        <div
          className="brand"
          style={{ cursor: 'pointer' }}
          onClick={() => onNavigate('landing')}
        >
          <div className="brand-icon">
            <Scale size={22} />
          </div>
          <div>
            <span>LawAid</span>
            <span style={{ fontSize: '0.65rem', display: 'block', color: '#0d9488', fontWeight: 600, letterSpacing: '0.05em' }}>
              JUDICIAL AID PLATFORM
            </span>
          </div>
        </div>

        {/* Navigation links */}
        <nav>
          <ul className="nav-links">
            <li>
              <button
                className={`nav-link ${activeTab === 'lawyers' ? 'active' : ''}`}
                onClick={() => onNavigate('lawyers')}
              >
                <Users size={16} />
                <span>Find Lawyers</span>
              </button>
            </li>

            {/* Admin Compliance Queue Link (SRS FR-38) */}
            <li>
              <button
                className={`nav-link ${activeTab === 'admin-verification' ? 'active' : ''}`}
                onClick={() => onNavigate('admin-verification')}
                style={{
                  color: activeTab === 'admin-verification' ? '#0f766e' : '#b45309',
                  backgroundColor: activeTab === 'admin-verification' ? '#ccfbf1' : '#fef3c7',
                  border: '1px solid #fde68a',
                }}
              >
                <ClipboardCheck size={16} />
                <span>Admin Verification Queue</span>
              </button>
            </li>

            {!currentUser && (
              <li>
                <button
                  className={`nav-link ${activeTab === 'register-lawyer' ? 'active' : ''}`}
                  onClick={() => onNavigate('register-lawyer')}
                >
                  <ShieldCheck size={16} color="#0d9488" />
                  <span>Lawyer Join</span>
                </button>
              </li>
            )}
          </ul>
        </nav>

        {/* User Status / Actions */}
        <div className="nav-user">
          {currentUser ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#0f172a' }}>
                  {currentUser.full_name}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', justifyContent: 'flex-end' }}>
                  {currentUser.role === 'admin' && (
                    <span className="badge badge-warning">Admin</span>
                  )}
                  {currentUser.role === 'client' && (
                    <span className="badge badge-info">Client</span>
                  )}
                  {isLawyer && (
                    <>
                      {currentUser.verification_status === 'approved' ? (
                        <VerifiedBadge size="sm" sanadNumber={currentUser.bar_council_no} />
                      ) : currentUser.verification_status === 'rejected' ? (
                        <span className="badge badge-danger">Rejected</span>
                      ) : (
                        <span className="badge badge-warning">Pending Review</span>
                      )}
                    </>
                  )}
                </div>
              </div>

              <button
                className="btn btn-secondary btn-sm"
                onClick={onLogout}
                title="Sign Out"
                style={{ padding: '0.45rem' }}
              >
                <LogOut size={16} />
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => onNavigate('login')}
              >
                <LogIn size={15} />
                <span>Sign In</span>
              </button>
              <button
                className="btn btn-primary btn-sm"
                onClick={() => onNavigate('role-select')}
              >
                <UserPlus size={15} />
                <span>Register</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
