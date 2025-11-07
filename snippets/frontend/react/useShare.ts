import { useState, useCallback } from 'react';

/**
 * Custom hook for Web Share API
 */
interface ShareData {
  title?: string;
  text?: string;
  url?: string;
}

interface UseShareReturn {
  share: (data: ShareData) => Promise<void>;
  isSupported: boolean;
  isSharing: boolean;
  error: Error | null;
}

export function useShare(): UseShareReturn {
  const [isSharing, setIsSharing] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const isSupported = typeof navigator !== 'undefined' && !!navigator.share;

  const share = useCallback(async (data: ShareData) => {
    if (!isSupported) {
      setError(new Error('Web Share API is not supported'));
      return;
    }

    setIsSharing(true);
    setError(null);

    try {
      await navigator.share(data);
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        setError(err as Error);
      }
    } finally {
      setIsSharing(false);
    }
  }, [isSupported]);

  return {
    share,
    isSupported,
    isSharing,
    error,
  };
}
