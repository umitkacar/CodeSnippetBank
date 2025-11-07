import { useEffect, useLayoutEffect } from 'react';

/**
 * useLayoutEffect that doesn't break SSR
 */
export const useIsomorphicLayoutEffect =
  typeof window !== 'undefined' ? useLayoutEffect : useEffect;

// Usage: Use this instead of useLayoutEffect to avoid SSR warnings
// useIsomorphicLayoutEffect(() => {
//   // Your layout effect code
// }, [dependencies]);
