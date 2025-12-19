"use client";

import { createContext, useContext } from "react";

interface AuthState {
  userId: string | null;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ 
  children, 
  value 
}: { 
  children: React.ReactNode; 
  value: AuthState;
}) {
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  
  if (context === null) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  
  return context;
}

