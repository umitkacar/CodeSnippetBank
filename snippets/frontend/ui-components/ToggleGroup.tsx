import React, { useState } from 'react';

interface ToggleGroupProps {
  options: { value: string; label: string }[];
  value?: string;
  onChange?: (value: string) => void;
}

export const ToggleGroup = ({ options, value: controlledValue, onChange }: ToggleGroupProps) => {
  const [internalValue, setInternalValue] = useState(options[0]?.value);
  const value = controlledValue !== undefined ? controlledValue : internalValue;

  const handleChange = (newValue: string) => {
    setInternalValue(newValue);
    onChange?.(newValue);
  };

  return (
    <div className="inline-flex rounded-md border">
      {options.map((option, index) => (
        <button
          key={option.value}
          onClick={() => handleChange(option.value)}
          className={`px-4 py-2 text-sm ${
            value === option.value
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 hover:bg-gray-50'
          } ${index === 0 ? 'rounded-l-md' : ''} ${
            index === options.length - 1 ? 'rounded-r-md' : 'border-r'
          }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
};
