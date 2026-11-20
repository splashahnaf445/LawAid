import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "./AuthContext";

import { ROLE_HOME, ROLE_LOGIN } from "./roles";


export default function ProtectedRoute({ roles }) {
  const { user, status } = useAuth();

  const location = useLocation();

  if (status === "loading"){
    return null;

  } 

  if (status === "anonymous"){
    return <Navigate to={ROLE_LOGIN[roles?.[0]] ?? "/role-access"} replace state={{ from: location }} />;

  }
    
 if (roles && !roles.includes(user.role)) {
    return <Navigate to={ROLE_HOME[user.role]} replace />;
 }
    
  return <Outlet />;
}