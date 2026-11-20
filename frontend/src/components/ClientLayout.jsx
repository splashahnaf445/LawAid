import {
     Link, 
    NavLink,
     Outlet,
      useNavigate
     } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

import usePageAssets from "../hooks/usePageAssets";


const LINKS = [["dashboard", "Dashboard"],
               ["find-lawyers", "Find Lawyers"],
                ["appointments", "Appointments"],
               ["messages", "Messages"], 
                  ["my-cases", "My Cases"], 
                  ["ai-assistant", "AI Assistant"], 
                  ["payments", "Payments"]];

const initials = (n = "") => n.split(" ").map((w) => w[0]).slice(0, 2).join("").toUpperCase();


export default function ClientLayout() {

  usePageAssets({ css: ["/assets/css/base.css", "/assets/css/client/shared.css"], bodyClass: "theme-client" });

  const { user, logout } = useAuth();

  const navigate = useNavigate();

  const onLogout = async (e) => {

    e.preventDefault();
    await logout();
    navigate("/client/login", { replace: true });
    
  };

  return (<>
    <header className="nav">
      <Link className="brand" to="/client/dashboard"><span className="logo">⚖</span>LawAid</Link>
      <nav className="links">
        {LINKS.map(([p, t]) => (
          <NavLink key={p} to={`/client/${p}`} className={({ isActive }) => (isActive ? "on" : undefined)}>{t}</NavLink>
        ))}
        <a href="/client/login" onClick={onLogout}>Log Out</a>
      </nav>
      <div className="user">
        {user.avatar_url ? <img src={user.avatar_url} alt="" /> :
          <span style={{ width: 32, height: 32, borderRadius: "50%", background: "#f59e0b", color: "#14213d", display: "grid", placeItems: "center", fontWeight: 700, fontSize: 12 }}>{initials(user.full_name)}</span>}
        <span>{user.full_name}<br /><small style={{ fontWeight: 400, color: "#94a3b8" }}>User</small></span>
      </div>
    </header>

    <Outlet />

    <footer>
      <div><div className="brand"><span className="logo">⚖</span>LawAid</div>
        <p style={{ marginTop: 14 }}><b>Chamber Address:</b> Supreme Court Bar Annex Building, Ramna, Dhaka 1000, Bangladesh</p>
        <p><b>Direct Line:</b> +880 1700-000000</p></div>
      <div><h4>Solutions</h4><Link to="/client/find-lawyers">Client Consultation</Link><Link to="/client/find-lawyers">Supreme Court Advocates</Link><Link to="/client/appointments">Hearing Date Tracking</Link><Link to="/client/payments">Fee &amp; Invoicing</Link></div>
      <div><h4>Company</h4><a href="#">About Us</a><a href="#">Our Advocates</a><a href="#">Contact Us</a></div>
      <div><h4>Resources</h4><a href="#">Help Center</a><Link to="/client/ai-assistant">AI Assistant Guide</Link></div>
      <div><h4>Legal</h4><a href="#">Privacy Policy</a><a href="#">Terms of Service</a><a href="#">Security</a></div>
    </footer>
  </>);
}
