import { onMounted, onUnmounted, Ref } from 'vue';

export function useClickOutside(
  target: Ref<HTMLElement | null>,
  callback: () => void
) {
  const handler = (event: MouseEvent) => {
    if (target.value && !target.value.contains(event.target as Node)) {
      callback();
    }
  };

  onMounted(() => {
    document.addEventListener('mousedown', handler);
  });

  onUnmounted(() => {
    document.removeEventListener('mousedown', handler);
  });
}
