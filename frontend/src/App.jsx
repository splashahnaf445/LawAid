import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Landing from './pages/Landing';
import Lawyers from './pages/Lawyers';
import AdminVerification from './pages/AdminVerification';
import Login from './pages/Login';
import RoleSelect from './pages/RoleSelect';
import RegisterClient from './pages/RegisterClient';
import RegisterLawyer from './pages/RegisterLawyer';
import { authStorage } from './api/http';
import { login, getCurrentUser, logout } from './api/auth';
import { Scale, ShieldCheck, Lock } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('landing');
  const [currentUser, setCurrentUser] = useState(() => authStorage.getUser());

  // Check and refresh user session on load
  useEffect(() => {
    const token = authStorage.getToken();
    if (token) {
      getCurrentUser()
        .then((user) => setCurrentUser(user))
        .catch(() => {
          // Token expired or invalid
          authStorage.clearAll();
          setCurrentUser(null);
        });
    }

    const handleAuthExpired = () => {
      setCurrentUser(null);
      setActiveTab('login');
    };

    window.addEventListener('lawaid:auth_expired', handleAuthExpired);
    return () => {
      window.removeEventListener('lawaid:auth_expired', handleAuthExpired);
    };
  }, []);

  const handleNavigate = (tab) => {
    setActiveTab(tab);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    if (user.role === 'admin' || user.is_admin) {
      setActiveTab('admin-verification');
    } else {
      setActiveTab('lawyers');
    }
  };

  const handleLogout = () => {
    logout();
    setCurrentUser(null);
    setActiveTab('landing');
  };

  const handleLoginAsAdmin = async () => {
    try {
      const data = await login('admin@lawaid.gov.bd', 'AdminPass123!');
      setCurrentUser(data.user);
      setActiveTab('admin-verification');
    } catch (e) {
      alert('Could not auto-login as admin. Please sign in via the login page.');
      setActiveTab('login');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Platform Navigation */}
      <Navbar
        currentUser={currentUser}
        activeTab={activeTab}
        onNavigate={handleNavigate}
        onLogout={handleLogout}
      />

      {/* Main Routed Page Content */}
      <main style={{ flex: 1 }}>
        {activeTab === 'landing' && <Landing onNavigate={handleNavigate} />}
        {activeTab === 'lawyers' && <Lawyers onNavigate={handleNavigate} />}
        {activeTab === 'admin-verification' && (
          <AdminVerification
            currentUser={currentUser}
            onNavigate={handleNavigate}
            onLoginAsAdmin={handleLoginAsAdmin}
          />
        )}
        {activeTab === 'login' && (
          <Login
            onLoginSuccess={handleLoginSuccess}
            onNavigate={handleNavigate}
          />
        )}
        {activeTab === 'role-select' && (
          <RoleSelect
            onSelectRole={(role) => handleNavigate(role === 'lawyer' ? 'register-lawyer' : 'register-client')}
            onNavigate={handleNavigate}
          />
        )}
        {activeTab === 'register-client' && (
          <RegisterClient
            onRegisterSuccess={() => setActiveTab('login')}
            onNavigate={handleNavigate}
          />
        )}
        {activeTab === 'register-lawyer' && (
          <RegisterLawyer onNavigate={handleNavigate} />
        )}
      </main>

      {/* Footer */}
      <footer style={{ background: '#0f172a', color: '#94a3b8', borderTop: '1px solid #1e293b', padding: '2.5rem 0 1.5rem', marginTop: 'auto' }}>
        <div className="container">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1.5rem', marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#ffffff', fontWeight: 800, fontSize: '1.15rem' }}>
              <div style={{ width: 32, height: 32, borderRadius: 8, background: '#0d9488', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#ffffff' }}>
                <Scale size={18} />
              </div>
              <span>LawAid</span>
              <span style={{ fontSize: '0.7rem', color: '#2dd4bf', fontWeight: 600, border: '1px solid #134e4a', padding: '1px 6px', borderRadius: '4px' }}>
                Judicial Network
              </span>
            </div>

            <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.85rem' }}>
              <button
                onClick={() => handleNavigate('lawyers')}
                style={{ background: 'transparent', color: '#94a3b8', cursor: 'pointer' }}
              >
                Lawyer Directory (FR-3)
              </button>
              <button
                onClick={() => handleNavigate('register-lawyer')}
                style={{ background: 'transparent', color: '#94a3b8', cursor: 'pointer' }}
              >
                Advocate Verification (FR-2)
              </button>
              <button
                onClick={() => handleNavigate('admin-verification')}
                style={{ background: 'transparent', color: '#f59e0b', cursor: 'pointer' }}
              >
                Admin Verification Queue (FR-38)
              </button>
            </div>
          </div>

          <div style={{ borderTop: '1px solid #1e293b', paddingTop: '1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem', fontSize: '0.75rem', color: '#64748b' }}>
            <div>
              LawAid Software Engineering Project • Implements SRS Requirements: <strong>FR-2</strong> (NID & Bar Council upload), <strong>FR-3</strong> (Verification badge & search visibility), <strong>NFR-4</strong> (Encrypted document storage).
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                <Lock size={12} color="#0d9488" /> Fernet AES-128
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                <ShieldCheck size={12} color="#0d9488" /> Bar Council Verified
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
