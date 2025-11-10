import React, { useState } from 'react';

interface DatePickerProps {
  value?: string;
  onChange?: (date: string) => void;
}

export const DatePicker = ({ value: controlledValue, onChange }: DatePickerProps) => {
  const [internalValue, setInternalValue] = useState('');
  const value = controlledValue !== undefined ? controlledValue : internalValue;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInternalValue(newValue);
    onChange?.(newValue);
  };

  return (
    <input
      type="date"
      value={value}
      onChange={handleChange}
      className="rounded-md border px-3 py-2"
    />
  );
};
