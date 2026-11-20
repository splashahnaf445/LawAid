import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar.jsx'

export default function RoleSelect() {
  return (
    <>
      <Navbar />
      <main className="pd">
        <div className="portal">
          <h1>How will you use LawAid?</h1>
          <p>Pick the account that fits. You can’t change it later, so choose carefully.</p>
          <div className="choices">
            <Link to="/register/client">
              <b>I need legal help</b>
              <span>Find verified advocates, book consultations, track cases and payments.</span>
            </Link>
            <Link to="/register/lawyer">
              <b>I’m an advocate</b>
              <span>Manage appointments, clients and cases. Bar Council verification required.</span>
            </Link>
          </div>
          <p className="already">Already have an account? <Link to="/login">Log in</Link></p>
        </div>
      </main>
    </>
  )
}
