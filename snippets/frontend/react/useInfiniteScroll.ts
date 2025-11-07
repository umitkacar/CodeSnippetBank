import { useEffect, useRef, useCallback } from 'react';

/**
 * Custom hook for infinite scroll
 * @param callback - Function to call when reaching bottom
 * @param isFetching - Whether data is currently being fetched
 * @returns ref to attach to sentinel element
 */
export function useInfiniteScroll(
  callback: () => void,
  isFetching: boolean
) {
  const observer = useRef<IntersectionObserver | null>(null);

  const lastElementRef = useCallback(
    (node: HTMLElement | null) => {
      if (isFetching) return;

      if (observer.current) observer.current.disconnect();

      observer.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
          callback();
        }
      });

      if (node) observer.current.observe(node);
    },
    [callback, isFetching]
  );

  return lastElementRef;
}

// Usage:
// const lastItemRef = useInfiniteScroll(() => loadMore(), isLoading);
// <div ref={lastItemRef}>Last item</div>
