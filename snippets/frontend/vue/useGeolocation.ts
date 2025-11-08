import { ref, onMounted, onUnmounted } from 'vue';

export function useGeolocation() {
  const latitude = ref<number | null>(null);
  const longitude = ref<number | null>(null);
  const error = ref<string | null>(null);
  const loading = ref(true);

  let watchId: number | null = null;

  onMounted(() => {
    if ('geolocation' in navigator) {
      watchId = navigator.geolocation.watchPosition(
        (position) => {
          latitude.value = position.coords.latitude;
          longitude.value = position.coords.longitude;
          loading.value = false;
        },
        (err) => {
          error.value = err.message;
          loading.value = false;
        }
      );
    } else {
      error.value = 'Geolocation is not supported';
      loading.value = false;
    }
  });

  onUnmounted(() => {
    if (watchId !== null) {
      navigator.geolocation.clearWatch(watchId);
    }
  });

  return { latitude, longitude, error, loading };
}
