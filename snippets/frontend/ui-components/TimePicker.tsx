import React, { useState } from 'react';

interface TimePickerProps {
  value?: string;
  onChange?: (time: string) => void;
}

export const TimePicker = ({ value: controlledValue, onChange }: TimePickerProps) => {
  const [internalValue, setInternalValue] = useState('12:00');
  const value = controlledValue !== undefined ? controlledValue : internalValue;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInternalValue(newValue);
    onChange?.(newValue);
  };

  return (
    <input
      type="time"
      value={value}
      onChange={handleChange}
      className="rounded-md border px-3 py-2"
    />
  );
};
