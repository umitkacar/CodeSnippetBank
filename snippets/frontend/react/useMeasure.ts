import { useState, useEffect, useRef, RefObject } from 'react';

/**
 * Custom hook to measure element dimensions
 */
interface Dimensions {
  width: number;
  height: number;
  top: number;
  left: number;
  x: number;
  y: number;
  right: number;
  bottom: number;
}

export function useMeasure<T extends HTMLElement = HTMLElement>(): [
  RefObject<T>,
  Dimensions
] {
  const ref = useRef<T>(null);
  const [dimensions, setDimensions] = useState<Dimensions>({
    width: 0,
    height: 0,
    top: 0,
    left: 0,
    x: 0,
    y: 0,
    right: 0,
    bottom: 0,
  });

  useEffect(() => {
    if (!ref.current) return;

    const observer = new ResizeObserver((entries) => {
      if (entries[0]) {
        const { width, height, top, left, x, y, right, bottom } =
          entries[0].target.getBoundingClientRect();
        setDimensions({ width, height, top, left, x, y, right, bottom });
      }
    });

    observer.observe(ref.current);

    return () => {
      observer.disconnect();
    };
  }, []);

  return [ref, dimensions];
}
