import React, { useState } from 'react';

interface CalendarProps {
  value?: Date;
  onChange?: (date: Date) => void;
}

export const Calendar = ({ value: controlledValue, onChange }: CalendarProps) => {
  const [internalValue, setInternalValue] = useState(new Date());
  const value = controlledValue || internalValue;

  const daysInMonth = new Date(
    value.getFullYear(),
    value.getMonth() + 1,
    0
  ).getDate();
  const firstDay = new Date(value.getFullYear(), value.getMonth(), 1).getDay();

  const days = Array.from({ length: daysInMonth }, (_, i) => i + 1);

  const handleDateClick = (day: number) => {
    const newDate = new Date(value.getFullYear(), value.getMonth(), day);
    setInternalValue(newDate);
    onChange?.(newDate);
  };

  return (
    <div className="w-64 rounded-md border bg-white p-4">
      <div className="mb-4 text-center font-semibold">
        {value.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
      </div>
      <div className="grid grid-cols-7 gap-1 text-center text-sm">
        {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map((day) => (
          <div key={day} className="font-medium text-gray-500">
            {day}
          </div>
        ))}
        {Array.from({ length: firstDay }).map((_, i) => (
          <div key={`empty-${i}`} />
        ))}
        {days.map((day) => (
          <button
            key={day}
            onClick={() => handleDateClick(day)}
            className={`rounded p-2 hover:bg-gray-100 ${
              day === value.getDate() ? 'bg-blue-600 text-white' : ''
            }`}
          >
            {day}
          </button>
        ))}
      </div>
    </div>
  );
};
