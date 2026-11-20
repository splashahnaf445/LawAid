import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import VerifiedBadge from './VerifiedBadge.jsx'

/**
 * Site header.
 * Integration note (integration/merge-all): Usama's navbar (prototype styling) with the
 * navigation and signed-in user status from Ahnaf's navbar: lawyer directory, admin
 * verification queue, "Lawyer join", user name + role / verification badge, sign out.
 * The user comes from Saker's useAuth() - the one login flow.
 */
function UserStatus({ user }) {
  if (user.role === 'admin' || user.is_admin) return <span className="pill">Admin</span>
  if (user.role === 'client') return <span className="pill g">Client</span>
  if (user.verification_status === 'approved') {
    return <VerifiedBadge size="sm" sanadNumber={user.bar_council_no} />
  }
  if (user.verification_status === 'rejected') return <span className="pill r">Rejected</span>
  return <span className="pill">Pending review</span>
}

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const linkClass = ({ isActive }) => (isActive ? 'on' : undefined)

  async function signOut() {
    await logout()
    navigate('/')
  }

  return (
    <header className="nav">
      <Link to="/" className="brand">
        <span className="logo" aria-hidden="true">⚖</span> LawAid
      </Link>
      <nav className="links" aria-label="Main">
        <NavLink to="/lawyers" className={linkClass}>Find lawyers</NavLink>
        <NavLink to="/admin/verification" className={linkClass}>Admin verification queue</NavLink>
        {!user && <NavLink to="/register/lawyer" className={linkClass}>Lawyer join</NavLink>}
      </nav>
      {user ? (
        <div className="user">
          <span>{user.full_name}</span>
          <UserStatus user={user} />
          <button type="button" className="btn ghost sm" onClick={signOut}>Sign out</button>
        </div>
      ) : (
        <div className="user">
          <Link to="/login" className="btn ghost sm">Log in</Link>
          <Link to="/register" className="btn sm">Create account</Link>
        </div>
      )}
    </header>
  )
}
