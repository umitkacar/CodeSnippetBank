import { useState, useEffect } from 'react';

/**
 * Custom hook to detect user idle state
 * @param timeout - Idle timeout in milliseconds
 * @returns Boolean indicating if user is idle
 */
export function useIdle(timeout: number = 60000): boolean {
  const [isIdle, setIsIdle] = useState(false);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;

    const handleActivity = () => {
      setIsIdle(false);
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => setIsIdle(true), timeout);
    };

    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];

    events.forEach((event) => {
      document.addEventListener(event, handleActivity);
    });

    timeoutId = setTimeout(() => setIsIdle(true), timeout);

    return () => {
      events.forEach((event) => {
        document.removeEventListener(event, handleActivity);
      });
      clearTimeout(timeoutId);
    };
  }, [timeout]);

  return isIdle;
}
