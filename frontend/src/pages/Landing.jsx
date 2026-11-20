import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar.jsx'

export default function Landing() {
  return (
    <>
      <Navbar />
      <main className="pd">
        <div className="portal">
          <span className="logo" aria-hidden="true" style={{ width: 56, height: 56, fontSize: 26 }}>⚖</span>
          <h1>LawAid</h1>
          <p>Legal consultation and chamber management for Bangladesh. Find a verified advocate, or run your chamber from one place.</p>
          <div className="ctas">
            <Link to="/register" className="btn">Create an account</Link>
            <Link to="/login" className="btn ghost">Log in</Link>
            {/* Ahnaf (SYS-22): entry to the verified-lawyer directory */}
            <Link to="/lawyers" className="btn ghost">Find a verified lawyer</Link>
          </div>
        </div>
      </main>
    </>
  )
}
