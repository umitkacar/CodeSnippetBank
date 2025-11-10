import { ref, Ref, onMounted, onUnmounted } from 'vue';

export function useHover(target: Ref<HTMLElement | null>) {
  const isHovered = ref(false);

  const handleMouseEnter = () => (isHovered.value = true);
  const handleMouseLeave = () => (isHovered.value = false);

  onMounted(() => {
    if (target.value) {
      target.value.addEventListener('mouseenter', handleMouseEnter);
      target.value.addEventListener('mouseleave', handleMouseLeave);
    }
  });

  onUnmounted(() => {
    if (target.value) {
      target.value.removeEventListener('mouseenter', handleMouseEnter);
      target.value.removeEventListener('mouseleave', handleMouseLeave);
    }
  });

  return isHovered;
}
