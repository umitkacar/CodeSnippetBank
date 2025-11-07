import { useState, useCallback } from 'react';

/**
 * Custom hook for boolean state management
 */
export function useBoolean(initialValue: boolean = false) {
  const [value, setValue] = useState(initialValue);

  const setTrue = useCallback(() => setValue(true), []);
  const setFalse = useCallback(() => setValue(false), []);
  const toggle = useCallback(() => setValue((v) => !v), []);

  return {
    value,
    setValue,
    setTrue,
    setFalse,
    toggle,
  };
}
