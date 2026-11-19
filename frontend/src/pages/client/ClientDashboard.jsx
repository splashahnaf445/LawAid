import { Link } from "react-router-dom";
import { useAuth } from "../../auth/AuthContext";
import usePageAssets from "../../hooks/usePageAssets";


export default function ClientDashboard() {
  usePageAssets({ css: ["/assets/css/client/dashboard.css"] });
  const { user } = useAuth();
  return (
    <div className="cw">
      <div className="wl">
        <h1>Welcome back, {user.full_name.split(" ")[0]}</h1>
        <p>Overview of your legal consultations, chamber dates &amp; active court cases in Bangladesh judiciary courts.</p>
        <Link className="btn sm" to="/client/find-lawyers">Book Consultation →</Link>
      </div>
      <div className="ct">
        <div className="cc2"><small>TODAY'S SESSION</small><b className="n">01</b><small>● Adv. Rafiqul · 04:30 PM</small></div>
        <div className="cc2"><small>NOTIFICATIONS</small><b className="n">05</b><Link className="btn sm" to="/client/notifications">See Notifications</Link></div>
        <div className="cc2"><small>CASES SUBMITTED</small><b className="n">12</b><Link className="btn sm" to="/client/my-cases">Go to My Cases</Link></div>
        <div className="cc2"><small>TOTAL SPENT</small><b className="n">20,000 <small>BDT</small></b><small style={{ color: "#059669" }}>Across 5 verified sessions</small></div>
      </div>
    </div>
  );
}
