import { useState, useEffect } from 'react';

/**
 * Custom hook to track device orientation
 */
type OrientationType = 'portrait-primary' | 'portrait-secondary' | 'landscape-primary' | 'landscape-secondary';

interface OrientationState {
  angle: number;
  type: OrientationType;
}

export function useOrientation(): OrientationState {
  const [orientation, setOrientation] = useState<OrientationState>({
    angle: 0,
    type: 'portrait-primary',
  });

  useEffect(() => {
    const handleOrientationChange = () => {
      const screen = window.screen as any;
      const orientation = screen.orientation || screen.mozOrientation || screen.msOrientation;

      if (orientation) {
        setOrientation({
          angle: orientation.angle || 0,
          type: orientation.type || 'portrait-primary',
        });
      }
    };

    handleOrientationChange();

    window.addEventListener('orientationchange', handleOrientationChange);
    const screen = window.screen as any;
    screen.orientation?.addEventListener('change', handleOrientationChange);

    return () => {
      window.removeEventListener('orientationchange', handleOrientationChange);
      screen.orientation?.removeEventListener('change', handleOrientationChange);
    };
  }, []);

  return orientation;
}
