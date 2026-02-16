'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useAuth } from './AuthContext'; // Assume auth context exists

interface Suggestion {
  task_id: string;
  reason: string;
  urgency: 'high' | 'medium' | 'low';
  confidence: number;
}

interface AutonomyContextType {
  suggestions: Suggestion[];
  autonomyLevel: 'low' | 'medium' | 'high';
  isPolling: boolean;
  refreshSuggestions: () => Promise<void>;
  updateAutonomyLevel: (level: 'low' | 'medium' | 'high') => Promise<void>;
}

const AutonomyContext = createContext<AutonomyContextType | null>(null);

export const AutonomyProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [autonomyLevel, setAutonomyLevel] = useState<'low' | 'medium' | 'high'>('low');
  const [isPolling, setIsPolling] = useState(false);
  const { token } = useAuth();

  const refreshSuggestions = async () => {
    if (!token) return;
    setIsPolling(true);
    try {
      const response = await fetch('/api/monitor/ai/analyze', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      });
      const data = await response.json();
      setSuggestions(data.suggestions || []);
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
    } finally {
      setIsPolling(false);
    }
  };

  const updateAutonomyLevel = async (level: 'low' | 'medium' | 'high') => {
    if (!token) return;
    try {
      const response = await fetch('/api/monitor/settings', {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ autonomy_level: level }),
      });
      if (response.ok) {
        setAutonomyLevel(level);
      }
    } catch (error) {
      console.error('Failed to update autonomy level:', error);
    }
  };

  useEffect(() => {
    if (autonomyLevel !== 'low') {
      const interval = setInterval(refreshSuggestions, 5 * 60 * 1000); // Poll every 5 min
      return () => clearInterval(interval);
    }
  }, [autonomyLevel]);

  return (
    <AutonomyContext.Provider value={{
      suggestions, autonomyLevel, isPolling, refreshSuggestions, updateAutonomyLevel
    }}>
      {children}
    </AutonomyContext.Provider>
  );
};

export const useAutonomy = () => {
  const context = useContext(AutonomyContext);
  if (!context) throw new Error('useAutonomy must be used within AutonomyProvider');
  return context;
};