import { ref } from 'vue';

export function useClipboard() {
  const text = ref('');
  const copied = ref(false);

  const copy = async (value: string) => {
    try {
      await navigator.clipboard.writeText(value);
      text.value = value;
      copied.value = true;
      setTimeout(() => (copied.value = false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
      copied.value = false;
    }
  };

  return { text, copied, copy };
}
