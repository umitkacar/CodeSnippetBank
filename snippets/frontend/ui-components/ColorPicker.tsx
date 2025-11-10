import React, { useState } from 'react';

interface ColorPickerProps {
  value?: string;
  onChange?: (color: string) => void;
}

export const ColorPicker = ({ value: controlledValue, onChange }: ColorPickerProps) => {
  const [internalValue, setInternalValue] = useState('#000000');
  const value = controlledValue !== undefined ? controlledValue : internalValue;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInternalValue(newValue);
    onChange?.(newValue);
  };

  return (
    <div className="flex items-center gap-2">
      <input
        type="color"
        value={value}
        onChange={handleChange}
        className="h-10 w-20 cursor-pointer rounded border"
      />
      <input
        type="text"
        value={value}
        onChange={handleChange}
        className="rounded border px-3 py-2"
      />
    </div>
  );
};
