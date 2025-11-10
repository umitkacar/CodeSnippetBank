import React, { useState } from 'react';

interface SliderProps {
  min?: number;
  max?: number;
  value?: number;
  onChange?: (value: number) => void;
}

export const Slider = ({ min = 0, max = 100, value: controlledValue, onChange }: SliderProps) => {
  const [internalValue, setInternalValue] = useState(50);
  const value = controlledValue !== undefined ? controlledValue : internalValue;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = Number(e.target.value);
    setInternalValue(newValue);
    onChange?.(newValue);
  };

  return (
    <div className="w-full">
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={handleChange}
        className="w-full"
      />
      <div className="mt-1 text-center text-sm text-gray-600">{value}</div>
    </div>
  );
};
