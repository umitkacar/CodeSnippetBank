import { onMounted, onUnmounted } from 'vue';

export function useTimeout(callback: () => void, delay: number) {
  let timeoutId: ReturnType<typeof setTimeout>;

  onMounted(() => {
    timeoutId = setTimeout(callback, delay);
  });

  onUnmounted(() => {
    clearTimeout(timeoutId);
  });
}
