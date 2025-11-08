import { ref } from 'vue';

export function useVibrate() {
  const isSupported = ref('vibrate' in navigator);

  const vibrate = (pattern: number | number[]) => {
    if (isSupported.value) {
      navigator.vibrate(pattern);
    }
  };

  const stop = () => {
    if (isSupported.value) {
      navigator.vibrate(0);
    }
  };

  return { isSupported, vibrate, stop };
}
