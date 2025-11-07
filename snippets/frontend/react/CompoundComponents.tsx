import React, { createContext, useContext, useState, ReactNode } from 'react';

/**
 * Compound Components Pattern - Accordion Example
 */
interface AccordionContextType {
  activeIndex: number | null;
  setActiveIndex: (index: number | null) => void;
}

const AccordionContext = createContext<AccordionContextType | undefined>(undefined);

const useAccordionContext = () => {
  const context = useContext(AccordionContext);
  if (!context) {
    throw new Error('Accordion compound components must be used within Accordion');
  }
  return context;
};

interface AccordionProps {
  children: ReactNode;
  defaultIndex?: number | null;
}

export const Accordion: React.FC<AccordionProps> & {
  Item: typeof AccordionItem;
  Trigger: typeof AccordionTrigger;
  Content: typeof AccordionContent;
} = ({ children, defaultIndex = null }) => {
  const [activeIndex, setActiveIndex] = useState<number | null>(defaultIndex);

  return (
    <AccordionContext.Provider value={{ activeIndex, setActiveIndex }}>
      <div className="accordion">{children}</div>
    </AccordionContext.Provider>
  );
};

interface AccordionItemProps {
  children: ReactNode;
  index: number;
}

const AccordionItem: React.FC<AccordionItemProps> = ({ children, index }) => {
  return <div className="accordion-item" data-index={index}>{children}</div>;
};

interface AccordionTriggerProps {
  children: ReactNode;
  index: number;
}

const AccordionTrigger: React.FC<AccordionTriggerProps> = ({ children, index }) => {
  const { activeIndex, setActiveIndex } = useAccordionContext();

  const handleClick = () => {
    setActiveIndex(activeIndex === index ? null : index);
  };

  return (
    <button
      className="accordion-trigger"
      onClick={handleClick}
      aria-expanded={activeIndex === index}
    >
      {children}
    </button>
  );
};

interface AccordionContentProps {
  children: ReactNode;
  index: number;
}

const AccordionContent: React.FC<AccordionContentProps> = ({ children, index }) => {
  const { activeIndex } = useAccordionContext();
  const isActive = activeIndex === index;

  return (
    <div
      className="accordion-content"
      style={{ display: isActive ? 'block' : 'none' }}
    >
      {children}
    </div>
  );
};

Accordion.Item = AccordionItem;
Accordion.Trigger = AccordionTrigger;
Accordion.Content = AccordionContent;

// Usage:
// <Accordion>
//   <Accordion.Item index={0}>
//     <Accordion.Trigger index={0}>Section 1</Accordion.Trigger>
//     <Accordion.Content index={0}>Content 1</Accordion.Content>
//   </Accordion.Item>
// </Accordion>
