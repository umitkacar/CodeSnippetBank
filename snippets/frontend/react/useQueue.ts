import { useState, useCallback } from 'react';

/**
 * Custom hook for queue data structure
 */
export function useQueue<T>(initialValue: T[] = []) {
  const [queue, setQueue] = useState<T[]>(initialValue);

  const enqueue = useCallback((item: T) => {
    setQueue((q) => [...q, item]);
  }, []);

  const dequeue = useCallback(() => {
    let item: T | undefined;
    setQueue(([first, ...rest]) => {
      item = first;
      return rest;
    });
    return item;
  }, []);

  const peek = useCallback(() => {
    return queue[0];
  }, [queue]);

  const clear = useCallback(() => {
    setQueue([]);
  }, []);

  return {
    queue,
    enqueue,
    dequeue,
    peek,
    clear,
    size: queue.length,
    isEmpty: queue.length === 0,
  };
}
