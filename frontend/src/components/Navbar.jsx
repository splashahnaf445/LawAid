import { useEffect, useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { logout } from '../api/auth'
import { authStorage } from '../api/http'
import VerifiedBadge from './VerifiedBadge.jsx'

/**
 * Site header.
 * Integration note (integration/merge-all): Usama's navbar (prototype styling) with the
 * navigation and signed-in user status from Ahnaf's navbar: lawyer directory, admin
 * verification queue, "Lawyer join", user name + role / verification badge, sign out.
 */
function useStoredUser() {
  const [user, setUser] = useState(() => authStorage.getUser())
  useEffect(() => {
    const refresh = () => setUser(authStorage.getUser())
    window.addEventListener('lawaid:auth_changed', refresh)
    window.addEventListener('lawaid:auth_expired', refresh)
    window.addEventListener('storage', refresh)
    return () => {
      window.removeEventListener('lawaid:auth_changed', refresh)
      window.removeEventListener('lawaid:auth_expired', refresh)
      window.removeEventListener('storage', refresh)
    }
  }, [])
  return user
}

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
  const user = useStoredUser()
  const navigate = useNavigate()
  const linkClass = ({ isActive }) => (isActive ? 'on' : undefined)

  function signOut() {
    logout()
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
