import { Lock, Scale, ShieldCheck } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

/**
 * Ahnaf (SYS-21/22): footer from his App.jsx (feature/lawyer-verification-and-badge), moved into
 * its own component during integration and switched from tab navigation to routes.
 * Shown on the verification pages (lawyer directory, admin queue, login).
 */
export default function Footer() {
  const navigate = useNavigate()
  const go = (path) => {
    navigate(path)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
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
            <button onClick={() => go('/lawyers')} style={{ background: 'transparent', color: '#94a3b8', cursor: 'pointer' }}>
              Lawyer Directory (FR-3)
            </button>
            <button onClick={() => go('/register/lawyer')} style={{ background: 'transparent', color: '#94a3b8', cursor: 'pointer' }}>
              Advocate Verification (FR-2)
            </button>
            <button onClick={() => go('/admin/verification')} style={{ background: 'transparent', color: '#f59e0b', cursor: 'pointer' }}>
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
  )
}
