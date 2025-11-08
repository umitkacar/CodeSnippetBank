import React, { ReactNode } from 'react';

interface ToolbarProps {
  children: ReactNode;
}

export const Toolbar = ({ children }: ToolbarProps) => (
  <div className="flex items-center gap-2 border-b bg-white p-2">
    {children}
  </div>
);
