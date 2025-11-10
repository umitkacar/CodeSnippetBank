import React, { useState, ReactNode } from 'react';

interface ContextMenuProps {
  children: ReactNode;
  items: { label: string; onClick: () => void }[];
}

export const ContextMenu = ({ children, items }: ContextMenuProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });

  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault();
    setPosition({ x: e.clientX, y: e.clientY });
    setIsOpen(true);
  };

  return (
    <>
      <div onContextMenu={handleContextMenu}>{children}</div>
      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div
            className="fixed z-20 rounded-md border bg-white shadow-lg"
            style={{ left: position.x, top: position.y }}
          >
            {items.map((item, index) => (
              <button
                key={index}
                onClick={() => {
                  item.onClick();
                  setIsOpen(false);
                }}
                className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100"
              >
                {item.label}
              </button>
            ))}
          </div>
        </>
      )}
    </>
  );
};
