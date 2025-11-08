import { watch, onUnmounted } from 'vue';
import { Ref } from 'vue';

export function useTitle(title: Ref<string> | string) {
  const originalTitle = document.title;

  if (typeof title === 'string') {
    document.title = title;
  } else {
    watch(
      title,
      (newTitle) => {
        document.title = newTitle;
      },
      { immediate: true }
    );
  }

  onUnmounted(() => {
    document.title = originalTitle;
  });
}
