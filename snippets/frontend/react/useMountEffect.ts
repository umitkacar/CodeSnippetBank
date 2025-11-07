import { useEffect, EffectCallback } from 'react';

/**
 * useEffect that only runs on mount
 */
export function useMountEffect(effect: EffectCallback) {
  useEffect(() => {
    return effect();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
}

// Usage: Runs only once on mount
// useMountEffect(() => {
//   console.log('Component mounted');
// });
