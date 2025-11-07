import { useEffect, useRef } from 'react';

/**
 * Custom hook to update document title
 */
export function useTitle(title: string) {
  const previousTitle = useRef(document.title);

  useEffect(() => {
    document.title = title;

    return () => {
      document.title = previousTitle.current;
    };
  }, [title]);
}

// Usage:
// useTitle('My Page Title');
