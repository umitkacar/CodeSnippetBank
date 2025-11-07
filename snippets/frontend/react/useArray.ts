import { useState, useCallback } from 'react';

/**
 * Custom hook for array manipulation
 */
export function useArray<T>(initialValue: T[]) {
  const [array, setArray] = useState<T[]>(initialValue);

  const push = useCallback((element: T) => {
    setArray((a) => [...a, element]);
  }, []);

  const filter = useCallback((callback: (item: T, index: number) => boolean) => {
    setArray((a) => a.filter(callback));
  }, []);

  const update = useCallback((index: number, newElement: T) => {
    setArray((a) => [
      ...a.slice(0, index),
      newElement,
      ...a.slice(index + 1),
    ]);
  }, []);

  const remove = useCallback((index: number) => {
    setArray((a) => [...a.slice(0, index), ...a.slice(index + 1)]);
  }, []);

  const clear = useCallback(() => {
    setArray([]);
  }, []);

  return {
    array,
    set: setArray,
    push,
    filter,
    update,
    remove,
    clear,
  };
}
