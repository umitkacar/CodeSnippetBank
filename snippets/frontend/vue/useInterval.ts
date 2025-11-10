import { onMounted, onUnmounted, ref } from 'vue';

export function useInterval(callback: () => void, delay: number | null) {
  const savedCallback = ref(callback);
  let intervalId: ReturnType<typeof setInterval>;

  onMounted(() => {
    savedCallback.value = callback;

    if (delay !== null) {
      intervalId = setInterval(() => savedCallback.value(), delay);
    }
  });

  onUnmounted(() => {
    if (intervalId) {
      clearInterval(intervalId);
    }
  });
}
