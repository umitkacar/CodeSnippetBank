/**
 * Vue 3 Pinia Store Example - Todo Management
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

interface Todo {
  id: string;
  text: string;
  completed: boolean;
  createdAt: Date;
}

export const useTodoStore = defineStore('todos', () => {
  const todos = ref<Todo[]>([]);
  const filter = ref<'all' | 'active' | 'completed'>('all');

  const filteredTodos = computed(() => {
    switch (filter.value) {
      case 'active':
        return todos.value.filter((t) => !t.completed);
      case 'completed':
        return todos.value.filter((t) => t.completed);
      default:
        return todos.value;
    }
  });

  const activeCount = computed(() =>
    todos.value.filter((t) => !t.completed).length
  );

  function addTodo(text: string) {
    todos.value.push({
      id: Date.now().toString(),
      text,
      completed: false,
      createdAt: new Date(),
    });
  }

  function removeTodo(id: string) {
    todos.value = todos.value.filter((t) => t.id !== id);
  }

  function toggleTodo(id: string) {
    const todo = todos.value.find((t) => t.id === id);
    if (todo) {
      todo.completed = !todo.completed;
    }
  }

  function clearCompleted() {
    todos.value = todos.value.filter((t) => !t.completed);
  }

  return {
    todos,
    filter,
    filteredTodos,
    activeCount,
    addTodo,
    removeTodo,
    toggleTodo,
    clearCompleted,
  };
});
