"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError, type RegisterInput, type User } from "@/lib/api";

interface GoogleAuthOutcome {
  status: "logged_in" | "new_user";
  google_id?: string;
  email?: string;
  full_name?: string;
}

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (identifier: string, password: string) => Promise<void>;
  register: (input: RegisterInput) => Promise<void>;
  loginWithGoogle: (idToken: string) => Promise<GoogleAuthOutcome>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    api
      .me()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  async function login(identifier: string, password: string) {
    await api.login(identifier, password);
    const me = await api.me();
    setUser(me);
    router.push("/dashboard");
  }

  async function register(input: RegisterInput) {
    await api.register(input);
    const identifier = input.email ?? input.mobile_number;
    if (!identifier) throw new Error("Registration requires an email or mobile number");
    await login(identifier, input.password);
  }

  async function loginWithGoogle(idToken: string): Promise<GoogleAuthOutcome> {
    const result = await api.googleAuth(idToken);
    if (result.status === "logged_in") {
      const me = await api.me();
      setUser(me);
      router.push("/dashboard");
    }
    // "new_user": nothing to set yet — the caller sends the person into
    // registration with the identity fields this returned pre-filled.
    return {
      status: result.status,
      google_id: result.google_id,
      email: result.email,
      full_name: result.full_name,
    };
  }

  async function logout() {
    await api.logout();
    setUser(null);
    router.push("/login");
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, loginWithGoogle, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export { ApiError };
