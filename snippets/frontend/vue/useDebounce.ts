import { ref, watch } from 'vue';

export function useDebounce<T>(value: T, delay: number = 500) {
  const debouncedValue = ref<T>(value);
  let timeout: ReturnType<typeof setTimeout>;

  watch(
    () => value,
    (newValue) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        debouncedValue.value = newValue as any;
      }, delay);
    },
    { immediate: true }
  );

  return debouncedValue;
}
