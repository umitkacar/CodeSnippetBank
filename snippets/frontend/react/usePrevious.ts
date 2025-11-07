import { useEffect, useRef } from 'react';

/**
 * Custom hook to get previous value of a state or prop
 * @param value - Current value
 * @returns Previous value
 */
export function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>();

  useEffect(() => {
    ref.current = value;
  }, [value]);

  return ref.current;
}

// Usage example:
// const [count, setCount] = useState(0);
// const previousCount = usePrevious(count);
// console.log(`Current: ${count}, Previous: ${previousCount}`);
