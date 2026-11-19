import { 
    BrowserRouter, 
    Navigate, 
    Route, 
    Routes 
} from "react-router-dom";

import { 
    AuthProvider, 
    useAuth 
} from "./auth/AuthContext";
import { 
    ROLE_HOME 
} 
from "./auth/roles";

import ProtectedRoute from "./auth/ProtectedRoute";

import ClientLayout from "./components/ClientLayout";

import RoleAccess from "./pages/RoleAccess";

import PortalLogin from "./pages/PortalLogin";

import ClientDashboard from "./pages/client/ClientDashboard";

import { ComingSoon, PortalHome } from "./pages/Placeholders";


const CLIENT_PAGES = ["find-lawyers", "appointments", "messages", "my-cases", "ai-assistant", "payments", "notifications"];


function Home() {

  const { user, status } = useAuth();
  
  if (status === "loading") return null;
  return user ? <Navigate to={ROLE_HOME[user.role]} replace /> : <ComingSoon title="Landing page (index.html)" />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/role-access" element={<RoleAccess />} />
          <Route path="/client/login" element={<PortalLogin portal="client" />} />
          <Route path="/lawyer/login" element={<PortalLogin portal="lawyer" />} />
          <Route path="/admin/login" element={<PortalLogin portal="admin" />} />
          <Route path="/forgot-password" element={<ComingSoon title="Forgot password (FR-5)" />} />
          <Route path="/register" element={<ComingSoon title="Registration (FR-1)" />} />

          <Route element={<ProtectedRoute roles={["client"]} />}>
            <Route element={<ClientLayout />}>
              <Route path="/client/dashboard" element={<ClientDashboard />} />
              {CLIENT_PAGES.map((p) => <Route key={p} path={`/client/${p}`} element={<ComingSoon title={p} />} />)}
            </Route>
          </Route>
          <Route element={<ProtectedRoute roles={["lawyer"]} />}>
            <Route path="/lawyer/dashboard" element={<PortalHome title="Lawyer dashboard" />} />
          </Route>
          <Route element={<ProtectedRoute roles={["admin"]} />}>
            <Route path="/admin/dashboard" element={<PortalHome title="Admin dashboard" />} />
          </Route>

          <Route path="*" element={<ComingSoon title="Page not found" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
