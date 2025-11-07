import { useState, useEffect, RefObject } from 'react';

/**
 * Custom hook to detect if element is on screen
 * @param ref - Reference to the element
 * @param rootMargin - Root margin for intersection observer
 * @returns Boolean indicating if element is visible
 */
export function useOnScreen<T extends Element>(
  ref: RefObject<T>,
  rootMargin: string = '0px'
): boolean {
  const [isIntersecting, setIntersecting] = useState<boolean>(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        setIntersecting(entry.isIntersecting);
      },
      { rootMargin }
    );

    const currentRef = ref.current;
    if (currentRef) {
      observer.observe(currentRef);
    }

    return () => {
      if (currentRef) {
        observer.unobserve(currentRef);
      }
    };
  }, [ref, rootMargin]);

  return isIntersecting;
}
