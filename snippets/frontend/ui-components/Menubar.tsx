import React, { ReactNode } from 'react';

interface MenubarProps {
  items: { label: string; onClick?: () => void }[];
}

export const Menubar = ({ items }: MenubarProps) => (
  <div className="flex border-b bg-white">
    {items.map((item, index) => (
      <button
        key={index}
        onClick={item.onClick}
        className="px-4 py-2 text-sm hover:bg-gray-100"
      >
        {item.label}
      </button>
    ))}
  </div>
);
