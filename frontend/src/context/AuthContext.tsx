'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AuthContextType {
  token: string | null;
  userName: string | null;
  setAuth: (token: string | null, userName?: string | null) => void;
  isAuthenticated: boolean;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [token, setTokenState] = useState<string | null>(null);
  const [userName, setUserNameState] = useState<string | null>(null);

  useEffect(() => {
    // Load token and userName from localStorage on mount
    const storedToken = localStorage.getItem('token');
    const storedUserName = localStorage.getItem('userName');
    if (storedToken) {
      setTokenState(storedToken);
    }
    if (storedUserName) {
      setUserNameState(storedUserName);
    }
  }, []);

  const setAuth = (newToken: string | null, newUserName?: string | null) => {
    setTokenState(newToken);
    if (newToken) {
      localStorage.setItem('token', newToken);
    } else {
      localStorage.removeItem('token');
    }
    if (newUserName !== undefined) {
      setUserNameState(newUserName);
      if (newUserName) {
        localStorage.setItem('userName', newUserName);
      } else {
        localStorage.removeItem('userName');
      }
    }
  };

  const logout = () => {
    setAuth(null, null);
  };

  return (
    <AuthContext.Provider value={{ token, userName, setAuth, isAuthenticated: !!token, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
