import { createContext, useContext, useEffect, useMemo, useState } from "react";
import {
  REFRESH_KEY,
  TOKEN_KEY,
  USER_KEY,
} from "../api/client";
import { apiLogin, apiRegister } from "../api/services";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  });

  const [ready, setReady] = useState(true);

  useEffect(() => {
    if (user) {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    } else {
      localStorage.removeItem(USER_KEY);
    }
  }, [user]);

  function persistTokens(data) {
    if (data.access) localStorage.setItem(TOKEN_KEY, data.access);
    if (data.refresh) localStorage.setItem(REFRESH_KEY, data.refresh);
  }

  async function login(credentials) {
    const data = await apiLogin(credentials);
    persistTokens(data);
    setUser(data.user);
    return data.user;
  }

  async function register(payload) {
    const data = await apiRegister(payload);
    persistTokens(data);
    setUser(data.user);
    return data.user;
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
    setUser(null);
  }

  const value = useMemo(
    () => ({ user, ready, login, register, logout, isAuthenticated: !!user }),
    [user, ready]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
