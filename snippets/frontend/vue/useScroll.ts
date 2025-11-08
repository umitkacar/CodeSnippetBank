import { ref, onMounted, onUnmounted } from 'vue';

export function useScroll() {
  const x = ref(0);
  const y = ref(0);

  const update = () => {
    x.value = window.pageXOffset;
    y.value = window.pageYOffset;
  };

  onMounted(() => {
    update();
    window.addEventListener('scroll', update);
  });

  onUnmounted(() => {
    window.removeEventListener('scroll', update);
  });

  return { x, y };
}
