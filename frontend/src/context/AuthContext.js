import { createContext, useContext, useEffect, useState } from "react";
import * as authService from "../services/authService";
import * as userService from "../services/userService";
import { getModeForRole } from "../config/roles";
import { getModeById } from "../config/modes";

const AuthContext = createContext(null);

function isTokenExpired(token) {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.exp * 1000 < Date.now();
  } catch {
    return true;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (!token || isTokenExpired(token)) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      setLoading(false);
      return;
    }

    userService.getMe()
      .then(res => {
        const userData = res.data.data;
        setUser(userData);
        
        // Set mode based on user's role (store full mode object for consumers)
        const userMode = getModeForRole(userData.role);
        setMode(getModeById(userMode));

        // Store mode id in localStorage
        localStorage.setItem("nyayaai_mode", userMode);
      })
      .catch(() => {
        localStorage.clear();
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const login = async (email, password) => {
    const res = await authService.login(email, password);
    
    const { token, user: userData } = res.data.data;
    
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(userData));
    
    setUser(userData);
    
    // Set mode based on user's role (store full mode object for consumers)
    const userMode = getModeForRole(userData.role);
    setMode(getModeById(userMode));
    localStorage.setItem("nyayaai_mode", userMode);
    
    return userData;
  };

  const register = async (fullName, email, password, role) => {
    const res = await authService.register(fullName, email, password, role);
    
    const { token, user: userData } = res.data.data;
    
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(userData));
    
    setUser(userData);
    
    // Set mode based on user's role (store full mode object for consumers)
    const userMode = getModeForRole(userData.role);
    setMode(getModeById(userMode));
    localStorage.setItem("nyayaai_mode", userMode);
    
    return userData;
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    localStorage.removeItem("nyayaai_mode");
    setUser(null);
    setMode(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        mode,
        login,
        register,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
