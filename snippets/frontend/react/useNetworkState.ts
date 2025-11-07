import { useState, useEffect } from 'react';

interface NetworkState {
  online: boolean;
  downlink?: number;
  effectiveType?: string;
  rtt?: number;
  saveData?: boolean;
}

/**
 * Custom hook to track network status
 * @returns Network state information
 */
export function useNetworkState(): NetworkState {
  const [state, setState] = useState<NetworkState>(() => {
    return {
      online: navigator.onLine,
    };
  });

  useEffect(() => {
    const handleOnline = () => {
      setState((prevState) => ({ ...prevState, online: true }));
    };

    const handleOffline = () => {
      setState((prevState) => ({ ...prevState, online: false }));
    };

    const handleConnectionChange = () => {
      const connection = (navigator as any).connection;
      if (connection) {
        setState({
          online: navigator.onLine,
          downlink: connection.downlink,
          effectiveType: connection.effectiveType,
          rtt: connection.rtt,
          saveData: connection.saveData,
        });
      }
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    const connection = (navigator as any).connection;
    if (connection) {
      connection.addEventListener('change', handleConnectionChange);
      handleConnectionChange();
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      if (connection) {
        connection.removeEventListener('change', handleConnectionChange);
      }
    };
  }, []);

  return state;
}
