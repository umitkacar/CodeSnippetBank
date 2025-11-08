import React, { ReactNode } from 'react';

interface SheetProps {
  isOpen: boolean;
  onClose: () => void;
  children: ReactNode;
  side?: 'left' | 'right';
}

export const Sheet = ({ isOpen, onClose, children, side = 'right' }: SheetProps) => {
  if (!isOpen) return null;

  return (
    <>
      <div
        className="fixed inset-0 z-40 bg-black/50"
        onClick={onClose}
      />
      <div
        className={`fixed z-50 h-full w-80 bg-white p-6 shadow-xl ${
          side === 'right' ? 'right-0' : 'left-0'
        } top-0`}
      >
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-gray-500 hover:text-gray-700"
        >
          ×
        </button>
        {children}
      </div>
    </>
  );
};
