import { ref, watch } from 'vue';

export function useThrottle<T>(value: T, delay: number = 500) {
  const throttledValue = ref<T>(value);
  let lastRun = 0;

  watch(
    () => value,
    (newValue) => {
      const now = Date.now();
      if (now - lastRun >= delay) {
        throttledValue.value = newValue as any;
        lastRun = now;
      }
    },
    { immediate: true }
  );

  return throttledValue;
}
