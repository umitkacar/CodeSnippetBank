import React from 'react';

interface SeparatorProps {
  orientation?: 'horizontal' | 'vertical';
  className?: string;
}

export const Separator = ({ orientation = 'horizontal', className = '' }: SeparatorProps) => (
  <div
    className={`bg-gray-200 ${
      orientation === 'horizontal' ? 'h-px w-full' : 'h-full w-px'
    } ${className}`}
  />
);
