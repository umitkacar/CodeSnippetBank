import { ref, onMounted, onUnmounted } from 'vue';

export function useMediaQuery(query: string) {
  const matches = ref(false);

  onMounted(() => {
    const mediaQuery = window.matchMedia(query);
    matches.value = mediaQuery.matches;

    const handler = (event: MediaQueryListEvent) => {
      matches.value = event.matches;
    };

    mediaQuery.addEventListener('change', handler);

    onUnmounted(() => {
      mediaQuery.removeEventListener('change', handler);
    });
  });

  return matches;
}
