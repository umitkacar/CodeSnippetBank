import React, { ReactNode } from 'react';

interface MenuProps {
  children: ReactNode;
}

export const Menu = ({ children }: MenuProps) => (
  <div className="rounded-md border bg-white shadow-lg">
    {children}
  </div>
);

export const MenuItem = ({ children, onClick }: { children: ReactNode; onClick?: () => void }) => (
  <button
    onClick={onClick}
    className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100"
  >
    {children}
  </button>
);
