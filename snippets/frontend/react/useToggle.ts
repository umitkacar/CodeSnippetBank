import { useState, useCallback } from 'react';

/**
 * Custom hook for toggling boolean state
 * @param initialValue - Initial boolean value
 * @returns [value, toggle, setValue]
 */
export function useToggle(
  initialValue: boolean = false
): [boolean, () => void, (value: boolean) => void] {
  const [value, setValue] = useState(initialValue);

  const toggle = useCallback(() => {
    setValue((v) => !v);
  }, []);

  return [value, toggle, setValue];
}

// Usage example:
// const [isOpen, toggleOpen, setIsOpen] = useToggle(false);
