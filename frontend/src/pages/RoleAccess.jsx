import { Link } from "react-router-dom";
import usePageAssets from "../hooks/usePageAssets";


export default function RoleAccess() {
  usePageAssets({ css: ["/assets/css/role-access.css"] });
  return (
    <main className="access-screen">
      <section className="access-card" aria-labelledby="page-title">
        <header className="access-heading">
          <h1 id="page-title">Welcome to LawAid</h1>
          <p>Select your role to access the legal management &amp; judicial consultation system</p>
        </header>

        <div className="access-roles">
          <Link className="access-role admin-role" to="/admin/login" aria-label="Continue to Chamber Admin login">
            <span className="role-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 2.8 20 6v5.3c0 5.1-3.4 8.5-8 10.1-4.6-1.6-8-5-8-10.1V6l8-3.2Z"/><path d="m8.5 11.8 2.2 2.2 4.8-5"/></svg></span>
            <small>INSTITUTIONAL LEVEL</small>
            <h2>Chamber Admin</h2>
            <p>Manage chamber operations, court cause list registries, advocate allocations, fee escrow, and platform system audit logs.</p>
            <b>Access Chamber <span>›</span></b>
          </Link>

          <Link className="access-role lawyer-role" to="/lawyer/login" aria-label="Continue to Advocate or Lawyer login">
            <span className="role-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 3v17M5 6h14M7 6l-4 8h8L7 6Zm10 0-4 8h8l-4-8ZM8 21h8"/></svg></span>
            <small>PRACTICE LEVEL</small>
            <h2>Advocate / Lawyer</h2>
            <p>Oversee daily court hearings, active case dockets, online video client consultations, and confidential evidence vaults.</p>
            <b>Enter Practice <span>›</span></b>
          </Link>

          <Link className="access-role client-role" to="/client/login" aria-label="Continue to Litigant or Client login">
            <span className="role-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="12" cy="7.5" r="3.5"/><path d="M5 21v-2.2a7 7 0 0 1 14 0V21Z"/></svg></span>
            <small>CLIENT &amp; CITIZEN LEVEL</small>
            <h2>Litigant / Client</h2>
            <p>Find verified Supreme Court &amp; District advocates, book instant consultations, track case status, and consult the legal assistant.</p>
            <b>Get Legal Aid <span>›</span></b>
          </Link>
        </div>

        <footer className="access-footer"><Link to="/">Back to home</Link></footer>
      </section>
    </main>
  );
}
