import { useEffect, EffectCallback } from 'react';

/**
 * useEffect that only runs once (even in React 18 Strict Mode)
 */
export function useEffectOnce(effect: EffectCallback) {
  useEffect(effect, []);
}

// Usage:
// useEffectOnce(() => {
//   console.log('This will run only once');
// });
