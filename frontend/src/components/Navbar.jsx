import { Link } from 'react-router-dom'

export default function Navbar() {
  return (
    <header className="nav">
      <Link to="/" className="brand">
        <span className="logo" aria-hidden="true">⚖</span> LawAid
      </Link>
      <div className="links" />
      <Link to="/login" className="btn ghost sm">Log in</Link>
    </header>
  )
}
