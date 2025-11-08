import { ref, onMounted } from 'vue';

export function usePermission(name: PermissionName) {
  const state = ref<PermissionState>('prompt');

  onMounted(async () => {
    try {
      const result = await navigator.permissions.query({ name });
      state.value = result.state;

      result.addEventListener('change', () => {
        state.value = result.state;
      });
    } catch (error) {
      console.error('Permission API error:', error);
    }
  });

  return state;
}
