import { useState, useEffect } from 'react';

/**
 * Custom hook to check browser permissions
 */
type PermissionName =
  | 'geolocation'
  | 'notifications'
  | 'push'
  | 'microphone'
  | 'camera'
  | 'midi'
  | 'background-sync'
  | 'persistent-storage'
  | 'accelerometer'
  | 'gyroscope'
  | 'magnetometer';

export function usePermission(permissionName: PermissionName) {
  const [state, setState] = useState<PermissionState | null>(null);

  useEffect(() => {
    let mounted = true;
    let permissionStatus: PermissionStatus | null = null;

    const onChange = () => {
      if (mounted && permissionStatus) {
        setState(permissionStatus.state);
      }
    };

    navigator.permissions
      .query({ name: permissionName as PermissionName })
      .then((status) => {
        permissionStatus = status;
        if (mounted) {
          setState(status.state);
          status.addEventListener('change', onChange);
        }
      })
      .catch((error) => {
        console.error('Permission query failed:', error);
      });

    return () => {
      mounted = false;
      if (permissionStatus) {
        permissionStatus.removeEventListener('change', onChange);
      }
    };
  }, [permissionName]);

  return state;
}
