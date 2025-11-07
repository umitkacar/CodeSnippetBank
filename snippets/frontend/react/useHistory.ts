import { useState, useCallback } from 'react';

/**
 * Custom hook for state history with undo/redo
 */
export function useHistory<T>(initialValue: T) {
  const [history, setHistory] = useState<T[]>([initialValue]);
  const [currentIndex, setCurrentIndex] = useState(0);

  const current = history[currentIndex];

  const set = useCallback(
    (value: T | ((current: T) => T)) => {
      const newValue = value instanceof Function ? value(current) : value;
      const newHistory = history.slice(0, currentIndex + 1);
      newHistory.push(newValue);
      setHistory(newHistory);
      setCurrentIndex(newHistory.length - 1);
    },
    [current, currentIndex, history]
  );

  const undo = useCallback(() => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  }, [currentIndex]);

  const redo = useCallback(() => {
    if (currentIndex < history.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  }, [currentIndex, history.length]);

  const clear = useCallback(() => {
    setHistory([initialValue]);
    setCurrentIndex(0);
  }, [initialValue]);

  const canUndo = currentIndex > 0;
  const canRedo = currentIndex < history.length - 1;

  return {
    value: current,
    set,
    undo,
    redo,
    clear,
    canUndo,
    canRedo,
    history,
  };
}
