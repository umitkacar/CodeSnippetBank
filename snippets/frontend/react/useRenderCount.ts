import { useRef, useEffect } from 'react';

/**
 * Custom hook to count component renders
 */
export function useRenderCount(): number {
  const renderCount = useRef(0);

  useEffect(() => {
    renderCount.current += 1;
  });

  return renderCount.current;
}

// Usage:
// const renderCount = useRenderCount();
// console.log(`Component rendered ${renderCount} times`);
