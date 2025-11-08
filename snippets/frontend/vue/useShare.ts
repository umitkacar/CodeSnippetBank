import { ref } from 'vue';

export function useShare() {
  const isSupported = ref('share' in navigator);

  const share = async (data: ShareData) => {
    if (!isSupported.value) {
      console.error('Web Share API not supported');
      return false;
    }

    try {
      await navigator.share(data);
      return true;
    } catch (error) {
      console.error('Share error:', error);
      return false;
    }
  };

  return { isSupported, share };
}
