import {
     useEffect, 
    useState
 } from "react";
import { 
    Link, 
    Navigate, 
    useLocation
 } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

import { ROLE_HOME } from "../auth/roles";

import usePageAssets from "../hooks/usePageAssets";

const LABELS = { 
    client: "USER LOGIN", 
    lawyer: "ADVOCATE LOGIN", 
    admin: "ADMIN LOGIN"
 };


const MESSAGES = {
  invalid_credentials: "Invalid email or password.",

  account_suspended: "Your account has been suspended. Please contact support.",

  account_pending_verification: "Your account is awaiting verification.",

  account_deactivated: "This account has been deactivated.",

  account_invited: "Your invitation has not been accepted yet.",

};


export default function PortalLogin({ portal }) {

  usePageAssets({

    css: ["/assets/css/base.css", "/assets/css/client/shared.css", "/assets/css/auth.css"],

    bodyClass: "theme-lawyer",    

  });
  const { login, user, status, sessionExpired } = useAuth();

  const location = useLocation();

  const [form, setForm] = useState({ email: "", password: "", remember: true });

  const [error, setError] = useState("");

  const [busy, setBusy] = useState(false);


  
  const [lockedUntil, setLockedUntil] = useState(0);

  const [now, setNow] = useState(Date.now());

  useEffect(() => {

    if (!lockedUntil) return;

    const t = setInterval(() => { setNow(Date.now()); if (Date.now() >= lockedUntil) setLockedUntil(0); }, 500);

    return () => clearInterval(t);

  }, [lockedUntil]);

  const secondsLeft = lockedUntil ? Math.max(0, Math.ceil((lockedUntil - now) / 1000)) : 0;


  
  if (status === "loading") {
    return null;
  }

  if (user) {

    const from = location.state?.from?.pathname;

    return <Navigate to={from?.startsWith(`/${user.role}/`) ? from : ROLE_HOME[user.role]} replace />;
  }

  const set = (k) => (e) =>
    setForm({ ...form, [k]: e.target.type === "checkbox" ? e.target.checked : e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    if (busy || secondsLeft > 0) return;
    setBusy(true); setError("");
    try {
      await login(form.email.trim(), form.password, { remember: form.remember, portal });
    } catch (err) {
      const res = err.response;
      if (res?.status === 429) {
        const wait = parseInt(res.headers["retry-after"], 10) || 60;
        setNow(Date.now()); setLockedUntil(Date.now() + wait * 1000);
      }
     else if (!res) {
        setError("Cannot reach the server. Check your connection.");
     }
      else {
        setError(MESSAGES[res.data?.code] ?? res.data?.detail ?? "Something went wrong. Please try again.");
      }
    } finally {
         setBusy(false); 
        }
  };

  const shownError = secondsLeft > 0 ? `Too many login attempts. Try again in ${secondsLeft}s.` : error;

  return (
    <div className="login"><div>
      <div className="lg"><i>⚖</i></div><h1>LawAid</h1>
      <div className="sub" style={{ fontSize: 10 }}>{LABELS[portal]}</div>
      <form className="lbox" onSubmit={submit} noValidate>
        <h2>Welcome back</h2><small>Please enter your credentials to access LawAid</small>
        {sessionExpired && !shownError && <div className="auth-alert warn" role="status">Your session expired. Please sign in again.</div>}
        {shownError && <div className="auth-alert error" role="alert">{shownError}</div>}

        <label htmlFor="email">EMAIL ADDRESS</label>
        <input id="email" type="email" autoComplete="username" required value={form.email}
               aria-invalid={!!error} onChange={set("email")} />
        <label htmlFor="password">PASSWORD <Link className="fp" to="/forgot-password">Forgot Password?</Link></label>
        <input id="password" type="password" autoComplete="current-password" required value={form.password}
               aria-invalid={!!error} onChange={set("password")} />

        <p style={{ textAlign: "left", marginTop: 16 }}>
          <label style={{ display: "flex", gap: 8, alignItems: "center", fontSize: 12, fontWeight: 400, letterSpacing: 0, margin: 0 }}>
            <input type="checkbox" checked={form.remember} onChange={set("remember")}
                   style={{ width: "auto", accentColor: "#f59e0b" }} /> Remember this device
          </label>
        </p>
        <button type="submit" className="btn" disabled={busy || secondsLeft > 0}>
          {busy ? "Signing in…" : secondsLeft > 0 ? `Try again in ${secondsLeft}s` : "Log In →"}
        </button>
        {portal !== "admin" && <p>Don't have an account? <Link to="/register">Create new account</Link></p>}
      </form>
      <Link className="back" to="/role-access">Return to LawAid Accessbase login →</Link>
    </div></div>
  );
}
