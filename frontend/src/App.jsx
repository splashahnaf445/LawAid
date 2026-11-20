/**
 * Routes.
 *
 * Integration note (integration/merge-all):
 *  - Router, landing and registration pages: Usama (main).
 *  - Login flow, portal logins, protected areas, client dashboard: Saker
 *    (feature/LAW-12-modular-architecture). His AuthProvider / useAuth is the ONE login flow;
 *    every page that needs the signed-in user reads it from there.
 *  - Lawyer directory, admin verification queue and the generic /login page: Ahnaf
 *    (feature/lawyer-verification-and-badge). His pages navigate with onNavigate('<tab>'),
 *    mapped to routes below, and render inside `.lv` so his light styles apply only to them.
 */
import { Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './auth/AuthContext'
import ProtectedRoute from './auth/ProtectedRoute'
import { ROLE_HOME } from './auth/roles'
import ClientLayout from './components/ClientLayout'
import Footer from './components/Footer.jsx'
import Navbar from './components/Navbar.jsx'
import AdminVerification from './pages/AdminVerification.jsx'
import Landing from './pages/Landing.jsx'
import Lawyers from './pages/Lawyers.jsx'
import Login from './pages/Login.jsx'
import { ComingSoon, PortalHome } from './pages/Placeholders'
import PortalLogin from './pages/PortalLogin'
import RegisterClient from './pages/RegisterClient.jsx'
import RegisterLawyer from './pages/RegisterLawyer.jsx'
import RoleAccess from './pages/RoleAccess'
import RoleSelect from './pages/RoleSelect.jsx'
import ClientDashboard from './pages/client/ClientDashboard'

// Saker: client portal pages that belong to later tasks
const CLIENT_PAGES = ['find-lawyers', 'appointments', 'messages', 'my-cases', 'ai-assistant', 'payments', 'notifications']

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

// Saker's Home (signed-in users go to their portal) showing Usama's landing page otherwise.
function Home() {
  const { user, status } = useAuth()
  if (status === 'loading') return null
  return user ? <Navigate to={ROLE_HOME[user.role]} replace /> : <Landing />
}

function AppRoutes() {
  const navigate = useNavigate()
  const { user, login } = useAuth()

  const onNavigate = (tab) => {
    navigate(TAB_PATHS[tab] ?? '/')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // Ahnaf: after login, admins go to the verification queue, everyone else to the directory.
  const handleLoginSuccess = (signedIn) => {
    navigate(signedIn.role === 'admin' || signedIn.is_admin ? '/admin/verification' : '/lawyers')
  }

  // Ahnaf: demo "log in as admin" button on the verification page.
  const handleLoginAsAdmin = async () => {
    try {
      handleLoginSuccess(await login('admin@lawaid.gov.bd', 'AdminPass123!'))
    } catch {
      alert('Could not auto-login as admin. Please sign in via the login page.')
      navigate('/login')
    }
  }

  return (
    <Routes>
      <Route path="/" element={<Home />} />

      {/* Usama (SYS-18): registration */}
      <Route path="/register" element={<RoleSelect />} />
      <Route path="/register/client" element={<RegisterClient />} />
      <Route path="/register/lawyer" element={<RegisterLawyer />} />

      {/* Saker (SYS-19): role chooser, portal logins, password reset placeholder */}
      <Route path="/role-access" element={<RoleAccess />} />
      <Route path="/client/login" element={<PortalLogin portal="client" />} />
      <Route path="/lawyer/login" element={<PortalLogin portal="lawyer" />} />
      <Route path="/admin/login" element={<PortalLogin portal="admin" />} />
      <Route path="/forgot-password" element={<ComingSoon title="Forgot password (FR-5)" />} />

      {/* Ahnaf (SYS-21/22): generic login, lawyer directory, admin verification queue */}
      <Route
        path="/login"
        element={<VerificationLayout><Login onLoginSuccess={handleLoginSuccess} onNavigate={onNavigate} /></VerificationLayout>}
      />
      <Route path="/lawyers" element={<VerificationLayout><Lawyers onNavigate={onNavigate} /></VerificationLayout>} />
      <Route
        path="/admin/verification"
        element={(
          <VerificationLayout>
            <AdminVerification currentUser={user} onNavigate={onNavigate} onLoginAsAdmin={handleLoginAsAdmin} />
          </VerificationLayout>
        )}
      />

      {/* Saker (SYS-19): protected areas */}
      <Route element={<ProtectedRoute roles={['client']} />}>
        <Route element={<ClientLayout />}>
          <Route path="/client/dashboard" element={<ClientDashboard />} />
          {CLIENT_PAGES.map((p) => <Route key={p} path={`/client/${p}`} element={<ComingSoon title={p} />} />)}
        </Route>
      </Route>
      <Route element={<ProtectedRoute roles={['lawyer']} />}>
        <Route path="/lawyer/dashboard" element={<PortalHome title="Lawyer dashboard" />} />
      </Route>
      <Route element={<ProtectedRoute roles={['admin']} />}>
        <Route path="/admin/dashboard" element={<PortalHome title="Admin dashboard" />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  )
}
