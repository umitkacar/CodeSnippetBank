import React, { ReactNode, useState } from 'react';

interface SidebarProps {
  children: ReactNode;
  isOpen?: boolean;
}

export const Sidebar = ({ children, isOpen: controlledIsOpen }: SidebarProps) => {
  const [internalIsOpen, setInternalIsOpen] = useState(true);
  const isOpen = controlledIsOpen !== undefined ? controlledIsOpen : internalIsOpen;

  return (
    <div
      className={`h-full bg-gray-100 transition-all duration-300 ${
        isOpen ? 'w-64' : 'w-0'
      } overflow-hidden`}
    >
      <div className="p-4">{children}</div>
    </div>
  );
};
