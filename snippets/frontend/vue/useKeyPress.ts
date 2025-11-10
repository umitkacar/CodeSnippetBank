import { ref, onMounted, onUnmounted } from 'vue';

export function useKeyPress(targetKey: string) {
  const keyPressed = ref(false);

  const downHandler = ({ key }: KeyboardEvent) => {
    if (key === targetKey) {
      keyPressed.value = true;
    }
  };

  const upHandler = ({ key }: KeyboardEvent) => {
    if (key === targetKey) {
      keyPressed.value = false;
    }
  };

  onMounted(() => {
    window.addEventListener('keydown', downHandler);
    window.addEventListener('keyup', upHandler);
  });

  onUnmounted(() => {
    window.removeEventListener('keydown', downHandler);
    window.removeEventListener('keyup', upHandler);
  });

  return keyPressed;
}
