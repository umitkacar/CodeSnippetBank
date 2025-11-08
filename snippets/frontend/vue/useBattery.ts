import { ref, onMounted } from 'vue';

export function useBattery() {
  const level = ref<number>(1);
  const charging = ref(false);
  const chargingTime = ref<number>(0);
  const dischargingTime = ref<number>(Infinity);

  onMounted(async () => {
    if ('getBattery' in navigator) {
      const battery = await (navigator as any).getBattery();

      level.value = battery.level;
      charging.value = battery.charging;
      chargingTime.value = battery.chargingTime;
      dischargingTime.value = battery.dischargingTime;

      battery.addEventListener('levelchange', () => {
        level.value = battery.level;
      });

      battery.addEventListener('chargingchange', () => {
        charging.value = battery.charging;
      });
    }
  });

  return { level, charging, chargingTime, dischargingTime };
}
