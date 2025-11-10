import { ref, onMounted, onUnmounted } from 'vue';

export function useOnline() {
  const online = ref(navigator.onLine);

  const handleOnline = () => (online.value = true);
  const handleOffline = () => (online.value = false);

  onMounted(() => {
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
  });

  onUnmounted(() => {
    window.removeEventListener('online', handleOnline);
    window.removeEventListener('offline', handleOffline);
  });

  return online;
}
