import React, { useState, ReactNode } from 'react';

interface HoverCardProps {
  trigger: ReactNode;
  content: ReactNode;
}

export const HoverCard = ({ trigger, content }: HoverCardProps) => {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div className="relative inline-block">
      <div
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
      >
        {trigger}
      </div>
      {isVisible && (
        <div className="absolute z-10 mt-2 w-64 rounded-md border bg-white p-4 shadow-lg">
          {content}
        </div>
      )}
    </div>
  );
};
