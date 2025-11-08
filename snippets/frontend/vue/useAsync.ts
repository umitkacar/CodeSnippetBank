import { ref, Ref } from 'vue';

export function useAsync<T>(asyncFunction: () => Promise<T>) {
  const data = ref<T | null>(null) as Ref<T | null>;
  const error = ref<Error | null>(null);
  const loading = ref(false);

  const execute = async () => {
    loading.value = true;
    error.value = null;
    try {
      data.value = await asyncFunction();
    } catch (e) {
      error.value = e as Error;
    } finally {
      loading.value = false;
    }
  };

  return { data, error, loading, execute };
}
