import React, { ReactNode } from 'react';

interface AlertProps {
  children: ReactNode;
  variant?: 'info' | 'success' | 'warning' | 'error';
  title?: string;
}

export const Alert = ({ children, variant = 'info', title }: AlertProps) => {
  const variants = {
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    success: 'bg-green-50 border-green-200 text-green-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    error: 'bg-red-50 border-red-200 text-red-800',
  };

  return (
    <div className={`rounded-md border p-4 ${variants[variant]}`}>
      {title && <h4 className="mb-1 font-medium">{title}</h4>}
      <div className="text-sm">{children}</div>
    </div>
  );
};
