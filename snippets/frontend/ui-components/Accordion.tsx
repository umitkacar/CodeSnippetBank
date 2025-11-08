import React, { useState, ReactNode } from 'react';

interface AccordionItem {
  id: string;
  title: string;
  content: ReactNode;
}

interface AccordionProps {
  items: AccordionItem[];
}

export const Accordion = ({ items }: AccordionProps) => {
  const [openItem, setOpenItem] = useState<string | null>(null);

  return (
    <div className="space-y-2">
      {items.map((item) => (
        <div key={item.id} className="border rounded-md">
          <button
            onClick={() => setOpenItem(openItem === item.id ? null : item.id)}
            className="flex w-full items-center justify-between p-4 text-left font-medium hover:bg-gray-50"
          >
            {item.title}
            <span>{openItem === item.id ? '−' : '+'}</span>
          </button>
          {openItem === item.id && (
            <div className="border-t p-4">{item.content}</div>
          )}
        </div>
      ))}
    </div>
  );
};
