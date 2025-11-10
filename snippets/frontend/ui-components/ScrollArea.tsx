import React, { ReactNode } from 'react';

interface ScrollAreaProps {
  children: ReactNode;
  height?: string;
}

export const ScrollArea = ({ children, height = '400px' }: ScrollAreaProps) => (
  <div
    className="overflow-auto"
    style={{ height }}
  >
    {children}
  </div>
);
