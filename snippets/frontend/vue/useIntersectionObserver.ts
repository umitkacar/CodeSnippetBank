import { ref, onMounted, onUnmounted, Ref } from 'vue';

export function useIntersectionObserver(
  target: Ref<HTMLElement | null>,
  options?: IntersectionObserverInit
) {
  const isIntersecting = ref(false);
  let observer: IntersectionObserver | null = null;

  onMounted(() => {
    if (target.value) {
      observer = new IntersectionObserver(([entry]) => {
        isIntersecting.value = entry.isIntersecting;
      }, options);

      observer.observe(target.value);
    }
  });

  onUnmounted(() => {
    if (observer) {
      observer.disconnect();
    }
  });

  return { isIntersecting };
}
