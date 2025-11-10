import React, { FormEvent, ReactNode } from 'react';

interface FormProps {
  onSubmit: (e: FormEvent<HTMLFormElement>) => void;
  children: ReactNode;
  className?: string;
}

export const Form = ({ onSubmit, children, className = '' }: FormProps) => (
  <form onSubmit={onSubmit} className={`space-y-4 ${className}`}>
    {children}
  </form>
);
