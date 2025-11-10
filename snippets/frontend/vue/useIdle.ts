import { ref, onMounted, onUnmounted } from 'vue';

export function useIdle(timeout: number = 60000) {
  const isIdle = ref(false);
  let timeoutId: ReturnType<typeof setTimeout>;

  const resetTimer = () => {
    isIdle.value = false;
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      isIdle.value = true;
    }, timeout);
  };

  onMounted(() => {
    const events = ['mousemove', 'mousedown', 'keypress', 'scroll', 'touchstart'];
    events.forEach((event) => {
      window.addEventListener(event, resetTimer);
    });
    resetTimer();
  });

  onUnmounted(() => {
    const events = ['mousemove', 'mousedown', 'keypress', 'scroll', 'touchstart'];
    events.forEach((event) => {
      window.removeEventListener(event, resetTimer);
    });
    clearTimeout(timeoutId);
  });

  return isIdle;
}
