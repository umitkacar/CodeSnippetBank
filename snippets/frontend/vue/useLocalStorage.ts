import { ref, watch } from 'vue';

export function useLocalStorage<T>(key: string, defaultValue: T) {
  const value = ref<T>(defaultValue);

  try {
    const item = window.localStorage.getItem(key);
    if (item) {
      value.value = JSON.parse(item);
    }
  } catch (error) {
    console.error(`Error loading ${key} from localStorage:`, error);
  }

  watch(
    value,
    (newValue) => {
      try {
        window.localStorage.setItem(key, JSON.stringify(newValue));
      } catch (error) {
        console.error(`Error saving ${key} to localStorage:`, error);
      }
    },
    { deep: true }
  );

  return value;
}
