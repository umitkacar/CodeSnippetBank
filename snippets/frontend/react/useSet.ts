import { useState, useCallback } from 'react';

/**
 * Custom hook for Set data structure
 */
export function useSet<T>(initialValues?: T[]) {
  const [set, setSet] = useState<Set<T>>(new Set(initialValues));

  const add = useCallback((value: T) => {
    setSet((prevSet) => new Set([...prevSet, value]));
  }, []);

  const remove = useCallback((value: T) => {
    setSet((prevSet) => {
      const newSet = new Set(prevSet);
      newSet.delete(value);
      return newSet;
    });
  }, []);

  const toggle = useCallback((value: T) => {
    setSet((prevSet) => {
      const newSet = new Set(prevSet);
      if (newSet.has(value)) {
        newSet.delete(value);
      } else {
        newSet.add(value);
      }
      return newSet;
    });
  }, []);

  const has = useCallback(
    (value: T) => {
      return set.has(value);
    },
    [set]
  );

  const clear = useCallback(() => {
    setSet(new Set());
  }, []);

  const reset = useCallback(() => {
    setSet(new Set(initialValues));
  }, [initialValues]);

  return {
    set,
    add,
    remove,
    toggle,
    has,
    clear,
    reset,
    size: set.size,
  };
}
