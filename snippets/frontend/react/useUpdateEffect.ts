import { useEffect, useRef, DependencyList, EffectCallback } from 'react';

/**
 * useEffect that skips the first render
 */
export function useUpdateEffect(effect: EffectCallback, deps?: DependencyList) {
  const isFirstMount = useRef(true);

  useEffect(() => {
    if (isFirstMount.current) {
      isFirstMount.current = false;
      return;
    }

    return effect();
  }, deps);
}

// Usage: Same as useEffect but doesn't run on mount
// useUpdateEffect(() => {
//   console.log('This runs on updates only');
// }, [value]);
