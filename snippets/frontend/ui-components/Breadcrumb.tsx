import React, { ReactNode } from 'react';

interface BreadcrumbProps {
  items: { label: ReactNode; href?: string }[];
}

export const Breadcrumb = ({ items }: BreadcrumbProps) => (
  <nav className="flex" aria-label="Breadcrumb">
    <ol className="inline-flex items-center space-x-1">
      {items.map((item, index) => (
        <li key={index} className="inline-flex items-center">
          {index > 0 && <span className="mx-2 text-gray-400">/</span>}
          {item.href ? (
            <a href={item.href} className="text-blue-600 hover:text-blue-700">
              {item.label}
            </a>
          ) : (
            <span className="text-gray-600">{item.label}</span>
          )}
        </li>
      ))}
    </ol>
  </nav>
);
