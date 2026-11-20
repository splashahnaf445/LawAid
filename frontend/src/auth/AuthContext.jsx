import {
     createContext, useCallback, useContext, useEffect, useMemo, useState 
    } from "react";

import { 
    api, authEvents, refreshSession 
} from "../api/client";

import { 
    setAccessToken 
} from "./tokenStore";

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);


export function AuthProvider({ children }) {

  const [user, setUser] = useState(null);

  const [status, setStatus] = useState("loading"); 

  const [sessionExpired, setSessionExpired] = useState(false);


  
  useEffect(() => {
    refreshSession()
      .then((d) => { 
        setUser(d.user); setStatus("authenticated"); 
    })

      .catch(() => setStatus("anonymous"));
  }, []);

  
  useEffect(() => {
    const onExpired = () => { 
        setUser(null); 
        setStatus("anonymous"); 
        setSessionExpired(true); 
    };

    authEvents.addEventListener("expired", onExpired);

    return () => authEvents.removeEventListener("expired", onExpired);
  }, []);


  const login = useCallback(async (email, password, { remember = true, portal } = {}) => {
    const { data } = await api.post("/auth/login/", { email, password, remember, portal });

    setAccessToken(data.access);

    setUser(data.user);

    setStatus("authenticated");
    setSessionExpired(false);

    return data.user;
  }, []);


  const logout = useCallback(async () => {

    try { await api.post("/auth/logout/"); }

    finally { 
        setAccessToken(null); 
        setUser(null);
         setStatus("anonymous");
         }
  }, []);

  const value = useMemo(() => ({ user, status, login, logout, sessionExpired }),

    [user, status, login, logout, sessionExpired]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
  
}
