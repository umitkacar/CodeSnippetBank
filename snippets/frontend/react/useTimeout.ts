import { useEffect, useRef } from 'react';

/**
 * Custom hook for setTimeout with cleanup
 */
export function useTimeout(callback: () => void, delay: number | null): void {
  const savedCallback = useRef(callback);

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    if (delay === null) {
      return;
    }

    const id = setTimeout(() => savedCallback.current(), delay);

    return () => clearTimeout(id);
  }, [delay]);
}

// Usage:
// useTimeout(() => {
//   console.log('Executed after 5 seconds');
// }, 5000);
