import React, { useState, ReactNode } from 'react';

interface CommandProps {
  children: ReactNode;
}

export const Command = ({ children }: CommandProps) => {
  const [search, setSearch] = useState('');

  return (
    <div className="rounded-md border bg-white">
      <input
        type="text"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Type a command or search..."
        className="w-full border-b px-4 py-3 focus:outline-none"
      />
      <div className="max-h-[300px] overflow-auto p-2">
        {children}
      </div>
    </div>
  );
};
