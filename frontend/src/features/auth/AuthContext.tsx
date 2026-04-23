import { createContext, useContext } from "react";
import type { ReactNode } from "react";
import type { User } from "../../types/user";
import { useAuth } from "./useAuth";

export interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  logout: (message?: string) => void;
  loginError: string | null;
  setLoginError: (error: string | null) => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuthContext(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuthContext must be used within AuthProvider");
  return ctx;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const auth = useAuth();
  return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>;
}
