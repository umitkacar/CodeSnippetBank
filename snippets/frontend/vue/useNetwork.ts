import { ref, onMounted, onUnmounted } from 'vue';

export function useNetwork() {
  const online = ref(navigator.onLine);
  const type = ref<string | undefined>(undefined);
  const downlink = ref<number | undefined>(undefined);
  const rtt = ref<number | undefined>(undefined);
  const saveData = ref<boolean | undefined>(undefined);

  const updateNetworkInfo = () => {
    online.value = navigator.onLine;
    const connection = (navigator as any).connection;
    if (connection) {
      type.value = connection.effectiveType;
      downlink.value = connection.downlink;
      rtt.value = connection.rtt;
      saveData.value = connection.saveData;
    }
  };

  onMounted(() => {
    updateNetworkInfo();
    window.addEventListener('online', updateNetworkInfo);
    window.addEventListener('offline', updateNetworkInfo);
  });

  onUnmounted(() => {
    window.removeEventListener('online', updateNetworkInfo);
    window.removeEventListener('offline', updateNetworkInfo);
  });

  return { online, type, downlink, rtt, saveData };
}
