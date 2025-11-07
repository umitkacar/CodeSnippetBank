import { useEffect, useRef } from 'react';

/**
 * Custom hook for debugging component lifecycle and props changes
 */
export function useLogger(componentName: string, props: any) {
  const previousProps = useRef<any>();

  useEffect(() => {
    console.log(`[${componentName}] Mounted`);

    return () => {
      console.log(`[${componentName}] Unmounted`);
    };
  }, [componentName]);

  useEffect(() => {
    if (previousProps.current) {
      const changedProps = Object.entries(props).reduce((acc, [key, value]) => {
        if (previousProps.current[key] !== value) {
          acc[key] = {
            from: previousProps.current[key],
            to: value,
          };
        }
        return acc;
      }, {} as any);

      if (Object.keys(changedProps).length > 0) {
        console.log(`[${componentName}] Props changed:`, changedProps);
      }
    }

    previousProps.current = props;
  });

  useEffect(() => {
    console.log(`[${componentName}] Props:`, props);
  }, [componentName, props]);
}

// Usage:
// useLogger('MyComponent', props);
