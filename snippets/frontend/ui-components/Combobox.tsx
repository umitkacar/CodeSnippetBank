import React, { useState } from 'react';

interface ComboboxOption {
  value: string;
  label: string;
}

interface ComboboxProps {
  options: ComboboxOption[];
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
}

export const Combobox = ({ options, value, onChange, placeholder = 'Select...' }: ComboboxProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');

  const filtered = options.filter((option) =>
    option.label.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="relative">
      <input
        type="text"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        onFocus={() => setIsOpen(true)}
        placeholder={placeholder}
        className="w-full rounded-md border px-3 py-2"
      />
      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute z-20 mt-1 max-h-60 w-full overflow-auto rounded-md border bg-white shadow-lg">
            {filtered.map((option) => (
              <div
                key={option.value}
                onClick={() => {
                  onChange?.(option.value);
                  setSearch(option.label);
                  setIsOpen(false);
                }}
                className="cursor-pointer px-3 py-2 hover:bg-gray-100"
              >
                {option.label}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};
