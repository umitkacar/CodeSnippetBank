import { useState, useCallback } from 'react';

interface ClipboardState {
  value: string | null;
  copy: (text: string) => Promise<void>;
  reset: () => void;
  error: Error | null;
  copied: boolean;
}

/**
 * Custom hook for clipboard operations
 * @param timeout - Time in ms before resetting copied state
 * @returns Clipboard state and operations
 */
export function useClipboard(timeout: number = 2000): ClipboardState {
  const [value, setValue] = useState<string | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [copied, setCopied] = useState(false);

  const copy = useCallback(
    async (text: string) => {
      try {
        await navigator.clipboard.writeText(text);
        setValue(text);
        setCopied(true);
        setError(null);

        setTimeout(() => {
          setCopied(false);
        }, timeout);
      } catch (err) {
        setError(err as Error);
        setCopied(false);
      }
    },
    [timeout]
  );

  const reset = useCallback(() => {
    setValue(null);
    setCopied(false);
    setError(null);
  }, []);

  return { value, copy, reset, error, copied };
}
