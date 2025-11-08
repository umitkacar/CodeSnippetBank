import React, { useState, ReactNode } from 'react';

interface CollapsibleProps {
  trigger: ReactNode;
  children: ReactNode;
  defaultOpen?: boolean;
}

export const Collapsible = ({ trigger, children, defaultOpen = false }: CollapsibleProps) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div>
      <div onClick={() => setIsOpen(!isOpen)} className="cursor-pointer">
        {trigger}
      </div>
      {isOpen && <div className="mt-2">{children}</div>}
    </div>
  );
};
