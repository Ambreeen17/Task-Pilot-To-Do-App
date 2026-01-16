import React, { createContext, useContext, useState, ReactNode } from 'react';
import { useAutonomy } from '../../context/AutonomyContext';

interface Toast {
  id: string;
  message: string;
  type: 'success' | 'warning' | 'error';
  duration?: number;
}

interface ToastContextType {
  addToast: (toast: Omit<Toast, 'id'>) => void;
}

const ToastContext = createContext<ToastContextType | null>(null);

export const ToastProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const { suggestions } = useAutonomy();

  const addToast = (toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36);
    setToasts(prev => [...prev, { id, ...toast }]);
    if (toast.duration) {
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== id));
      }, toast.duration);
    }
  };

  // Auto-notify new suggestions
  React.useEffect(() => {
    if (suggestions.length > 0) {
      addToast({
        message: `New AI suggestion: ${suggestions[0].reason}`,
        type: 'warning',
        duration: 10000
      });
    }
  }, [suggestions.length]);

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}
      <div className="fixed top-4 right-4 space-y-2 z-50">
        {toasts.map(toast => (
          <div key={toast.id} className={`p-4 rounded shadow-lg max-w-sm ${
            toast.type === 'success' ? 'bg-green-500' :
            toast.type === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
          } text-white`}>
            {toast.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) throw new Error('useToast must be used within ToastProvider');
  return context;
};