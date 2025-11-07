import { useState, useEffect } from 'react';

interface BatteryState {
  charging: boolean;
  chargingTime: number;
  dischargingTime: number;
  level: number;
  supported: boolean;
}

/**
 * Custom hook for battery status
 * @returns Battery state information
 */
export function useBattery(): BatteryState {
  const [state, setState] = useState<BatteryState>({
    charging: false,
    chargingTime: 0,
    dischargingTime: 0,
    level: 0,
    supported: false,
  });

  useEffect(() => {
    if (!('getBattery' in navigator)) {
      setState((s) => ({ ...s, supported: false }));
      return;
    }

    let battery: any;

    (navigator as any).getBattery().then((b: any) => {
      battery = b;

      const updateBatteryState = () => {
        setState({
          charging: battery.charging,
          chargingTime: battery.chargingTime,
          dischargingTime: battery.dischargingTime,
          level: battery.level,
          supported: true,
        });
      };

      updateBatteryState();

      battery.addEventListener('chargingchange', updateBatteryState);
      battery.addEventListener('chargingtimechange', updateBatteryState);
      battery.addEventListener('dischargingtimechange', updateBatteryState);
      battery.addEventListener('levelchange', updateBatteryState);
    });

    return () => {
      if (battery) {
        battery.removeEventListener('chargingchange', () => {});
        battery.removeEventListener('chargingtimechange', () => {});
        battery.removeEventListener('dischargingtimechange', () => {});
        battery.removeEventListener('levelchange', () => {});
      }
    };
  }, []);

  return state;
}
