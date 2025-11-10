import React, { ReactNode } from 'react';

interface AspectRatioProps {
  ratio?: number;
  children: ReactNode;
}

export const AspectRatio = ({ ratio = 16 / 9, children }: AspectRatioProps) => (
  <div style={{ position: 'relative', paddingBottom: `${100 / ratio}%` }}>
    <div style={{ position: 'absolute', inset: 0 }}>{children}</div>
  </div>
);
