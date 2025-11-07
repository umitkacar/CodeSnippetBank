import { useEffect, useRef } from 'react';

/**
 * Effect that only runs on unmount
 */
export function useUnmountEffect(fn: () => void) {
  const fnRef = useRef(fn);

  fnRef.current = fn;

  useEffect(() => {
    return () => {
      fnRef.current();
    };
  }, []);
}

// Usage: Runs only on unmount
// useUnmountEffect(() => {
//   console.log('Component will unmount');
// });
