import { ref, onUnmounted } from 'vue';

export function useWakeLock() {
  const isSupported = ref('wakeLock' in navigator);
  const isActive = ref(false);
  let wakeLock: any = null;

  const request = async () => {
    if (!isSupported.value) return;

    try {
      wakeLock = await (navigator as any).wakeLock.request('screen');
      isActive.value = true;

      wakeLock.addEventListener('release', () => {
        isActive.value = false;
      });
    } catch (error) {
      console.error('Wake Lock error:', error);
    }
  };

  const release = async () => {
    if (wakeLock) {
      await wakeLock.release();
      wakeLock = null;
      isActive.value = false;
    }
  };

  onUnmounted(() => {
    release();
  });

  return { isSupported, isActive, request, release };
}
