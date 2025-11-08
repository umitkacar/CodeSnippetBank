import React, { ReactNode } from 'react';

interface NavigationProps {
  items: { label: string; href: string; active?: boolean }[];
}

export const Navigation = ({ items }: NavigationProps) => (
  <nav className="flex space-x-4">
    {items.map((item, index) => (
      <a
        key={index}
        href={item.href}
        className={`px-3 py-2 rounded-md text-sm font-medium ${
          item.active
            ? 'bg-blue-600 text-white'
            : 'text-gray-700 hover:bg-gray-100'
        }`}
      >
        {item.label}
      </a>
    ))}
  </nav>
);
