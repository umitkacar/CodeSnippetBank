import { ref, onMounted, onUnmounted } from 'vue';

export function usePreferredDark() {
  const prefersDark = ref(false);

  onMounted(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    prefersDark.value = mediaQuery.matches;

    const handler = (event: MediaQueryListEvent) => {
      prefersDark.value = event.matches;
    };

    mediaQuery.addEventListener('change', handler);

    onUnmounted(() => {
      mediaQuery.removeEventListener('change', handler);
    });
  });

  return prefersDark;
}
