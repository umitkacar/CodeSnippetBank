import React, { useState, ReactNode } from 'react';

interface PopoverProps {
  trigger: ReactNode;
  content: ReactNode;
}

export const Popover = ({ trigger, content }: PopoverProps) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <div onClick={() => setIsOpen(!isOpen)}>{trigger}</div>
      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute z-20 mt-2 w-64 rounded-md border bg-white p-4 shadow-lg">
            {content}
          </div>
        </>
      )}
    </div>
  );
};
