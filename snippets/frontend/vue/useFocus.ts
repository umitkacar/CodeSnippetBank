import { ref, Ref, onMounted, onUnmounted } from 'vue';

export function useFocus(target: Ref<HTMLElement | null>) {
  const isFocused = ref(false);

  const handleFocus = () => (isFocused.value = true);
  const handleBlur = () => (isFocused.value = false);

  onMounted(() => {
    if (target.value) {
      target.value.addEventListener('focus', handleFocus);
      target.value.addEventListener('blur', handleBlur);
    }
  });

  onUnmounted(() => {
    if (target.value) {
      target.value.removeEventListener('focus', handleFocus);
      target.value.removeEventListener('blur', handleBlur);
    }
  });

  return isFocused;
}
