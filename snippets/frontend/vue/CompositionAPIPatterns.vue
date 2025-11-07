<!--
  Vue 3 Composition API Patterns
-->
<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';

// Reactive state
const count = ref(0);
const message = ref('Hello Vue 3!');

// Computed properties
const doubleCount = computed(() => count.value * 2);
const reversedMessage = computed(() =>
  message.value.split('').reverse().join('')
);

// Watchers
watch(count, (newValue, oldValue) => {
  console.log(`Count changed from ${oldValue} to ${newValue}`);
});

watch([count, message], ([newCount, newMessage]) => {
  console.log(`Multiple watchers: ${newCount}, ${newMessage}`);
});

// Methods
const increment = () => {
  count.value++;
};

const decrement = () => {
  count.value--;
};

// Lifecycle hooks
onMounted(() => {
  console.log('Component mounted');
});

onUnmounted(() => {
  console.log('Component unmounted');
});

// Props
interface Props {
  title?: string;
  initialCount?: number;
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Default Title',
  initialCount: 0,
});

// Emits
const emit = defineEmits<{
  (e: 'update', value: number): void;
  (e: 'save', data: string): void;
}>();

const handleUpdate = () => {
  emit('update', count.value);
};
</script>

<template>
  <div class="container">
    <h1>{{ props.title }}</h1>
    <p>Count: {{ count }}</p>
    <p>Double: {{ doubleCount }}</p>
    <p>Message: {{ message }}</p>
    <p>Reversed: {{ reversedMessage }}</p>

    <button @click="increment">Increment</button>
    <button @click="decrement">Decrement</button>
    <button @click="handleUpdate">Update</button>
  </div>
</template>

<style scoped>
.container {
  padding: 2rem;
}

button {
  margin: 0.5rem;
  padding: 0.5rem 1rem;
  cursor: pointer;
}
</style>
