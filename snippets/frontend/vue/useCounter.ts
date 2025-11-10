import { ref } from 'vue';

export function useCounter(initialValue: number = 0) {
  const count = ref(initialValue);

  const increment = () => count.value++;
  const decrement = () => count.value--;
  const reset = () => (count.value = initialValue);

  return { count, increment, decrement, reset };
}
