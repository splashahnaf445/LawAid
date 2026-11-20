/**
 * Routes.
 *
 * Integration note (integration/merge-all):
 *  - Router, landing and registration pages: Usama (main).
 *  - Lawyer directory, admin verification queue and login: Ahnaf
 *    (feature/lawyer-verification-and-badge). His pages navigate with onNavigate('<tab>'),
 *    which is mapped to routes below, and render inside the `.lv` wrapper so his
 *    light styles (styles/verification.css) apply only to them.
 *  - Usama's "/login" placeholder is replaced by Ahnaf's working Login page.
 */
import { useEffect, useState } from 'react'
import { Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { getCurrentUser, login } from './api/auth'
import { authStorage } from './api/http'
import Footer from './components/Footer.jsx'
import Navbar from './components/Navbar.jsx'
import AdminVerification from './pages/AdminVerification.jsx'
import Landing from './pages/Landing.jsx'
import Lawyers from './pages/Lawyers.jsx'
import Login from './pages/Login.jsx'
import RegisterClient from './pages/RegisterClient.jsx'
import RegisterLawyer from './pages/RegisterLawyer.jsx'
import RoleSelect from './pages/RoleSelect.jsx'

// Ahnaf's tab names -> routes
const TAB_PATHS = {
  landing: '/',
  lawyers: '/lawyers',
  'admin-verification': '/admin/verification',
  login: '/login',
  'role-select': '/register',
  'register-client': '/register/client',
  'register-lawyer': '/register/lawyer',
}

function VerificationLayout({ children }) {
  return (
    <>
      <Navbar />
      <div className="lv" style={{ display: 'flex', flexDirection: 'column' }}>
        <main style={{ flex: 1 }}>{children}</main>
        <Footer />
      </div>
    </>
  )
}

export default function App() {
  const navigate = useNavigate()
  const [currentUser, setCurrentUser] = useState(() => authStorage.getUser())

  const onNavigate = (tab) => {
    navigate(TAB_PATHS[tab] ?? '/')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // Ahnaf: refresh the session on load and react to expired tokens.
  useEffect(() => {
    if (authStorage.getToken()) {
      getCurrentUser()
        .then((user) => {
          setCurrentUser(user)
          window.dispatchEvent(new CustomEvent('lawaid:auth_changed', { detail: user }))
        })
        .catch(() => {
          authStorage.clearAll()
          setCurrentUser(null)
        })
    }
    const onExpired = () => {
      setCurrentUser(null)
      navigate('/login')
    }
    const onChanged = () => setCurrentUser(authStorage.getUser())
    window.addEventListener('lawaid:auth_expired', onExpired)
    window.addEventListener('lawaid:auth_changed', onChanged)
    return () => {
      window.removeEventListener('lawaid:auth_expired', onExpired)
      window.removeEventListener('lawaid:auth_changed', onChanged)
    }
  }, [navigate])

  const handleLoginSuccess = (user) => {
    setCurrentUser(user)
    window.dispatchEvent(new CustomEvent('lawaid:auth_changed', { detail: user }))
    navigate(user.role === 'admin' || user.is_admin ? '/admin/verification' : '/lawyers')
  }

  const handleLoginAsAdmin = async () => {
    try {
      const data = await login('admin@lawaid.gov.bd', 'AdminPass123!')
      handleLoginSuccess(data.user)
    } catch {
      alert('Could not auto-login as admin. Please sign in via the login page.')
      navigate('/login')
    }
  }

  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/register" element={<RoleSelect />} />
      <Route path="/register/client" element={<RegisterClient />} />
      <Route path="/register/lawyer" element={<RegisterLawyer />} />
      <Route
        path="/login"
        element={<VerificationLayout><Login onLoginSuccess={handleLoginSuccess} onNavigate={onNavigate} /></VerificationLayout>}
      />
      <Route path="/lawyers" element={<VerificationLayout><Lawyers onNavigate={onNavigate} /></VerificationLayout>} />
      <Route
        path="/admin/verification"
        element={(
          <VerificationLayout>
            <AdminVerification currentUser={currentUser} onNavigate={onNavigate} onLoginAsAdmin={handleLoginAsAdmin} />
          </VerificationLayout>
        )}
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
