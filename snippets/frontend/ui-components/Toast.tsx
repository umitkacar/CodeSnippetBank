import React, { ReactNode } from 'react';

interface ToastProps {
  message: ReactNode;
  variant?: 'success' | 'error' | 'info';
  onClose?: () => void;
}

export const Toast = ({ message, variant = 'info', onClose }: ToastProps) => {
  const variants = {
    success: 'bg-green-600',
    error: 'bg-red-600',
    info: 'bg-blue-600',
  };

  return (
    <div className={`fixed bottom-4 right-4 z-50 rounded-md px-6 py-4 text-white shadow-lg ${variants[variant]}`}>
      <div className="flex items-center gap-2">
        <span>{message}</span>
        {onClose && (
          <button onClick={onClose} className="ml-4 text-white hover:text-gray-200">
            ×
          </button>
        )}
      </div>
    </div>
  );
};
