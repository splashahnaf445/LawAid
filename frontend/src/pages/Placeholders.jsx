import { useState } from "react";
import { api } from "../api/client";
import { useAuth } from "../auth/AuthContext";


export function ComingSoon({ title }) {
  return <main style={{ padding: "60px 24px", textAlign: "center" }}><h1>{title}</h1><p>This screen belongs to another task.</p></main>;
}


export function PortalHome({ title }) {
  const { user, logout } = useAuth();
  const [out, setOut] = useState("");
  const ping = () => api.get("/auth/me/").then(
    (r) => setOut(JSON.stringify(r.data)),
    (e) => setOut(`Failed: ${e.response?.status}`)
  );
  return (
    <main style={{ padding: "60px 24px", textAlign: "center" }}>
      <h1>{title}</h1>
      <p>Signed in as {user.full_name} ({user.role})</p>
      <button onClick={ping}>Call protected API</button> <button onClick={logout}>Log out</button>
      <pre>{out}</pre>
    </main>
  );
}
