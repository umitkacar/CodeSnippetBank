import { useState, useEffect } from 'react';

/**
 * Custom hook to track document visibility
 */
export function useDocumentVisibility(): DocumentVisibilityState {
  const [visibility, setVisibility] = useState<DocumentVisibilityState>(
    document.visibilityState
  );

  useEffect(() => {
    const handleVisibilityChange = () => {
      setVisibility(document.visibilityState);
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  return visibility;
}

// Usage:
// const visibility = useDocumentVisibility();
// const isVisible = visibility === 'visible';
