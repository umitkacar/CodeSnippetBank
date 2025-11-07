// Vue Testing Library Examples
// Comprehensive VTL testing patterns for Vue components

import { render, screen, fireEvent, waitFor } from '@testing-library/vue';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { defineComponent, ref } from 'vue';

// Component examples
const ButtonComponent = defineComponent({
  name: 'ButtonComponent',
  props: {
    label: String,
  },
  emits: ['click'],
  template: '<button @click="$emit(\'click\')">{{ label }}</button>',
});

const CounterComponent = defineComponent({
  name: 'CounterComponent',
  setup() {
    const count = ref(0);

    const increment = () => count.value++;
    const decrement = () => count.value--;
    const reset = () => (count.value = 0);

    return { count, increment, decrement, reset };
  },
  template: `
    <div>
      <p>Count: {{ count }}</p>
      <button @click="increment">Increment</button>
      <button @click="decrement">Decrement</button>
      <button @click="reset">Reset</button>
    </div>
  `,
});

const SearchComponent = defineComponent({
  name: 'SearchComponent',
  setup() {
    const query = ref('');
    const results = ref<string[]>([]);

    const search = () => {
      results.value = [`Result for "${query.value}"`];
    };

    return { query, results, search };
  },
  template: `
    <div>
      <form @submit.prevent="search">
        <label for="search">Search:</label>
        <input
          id="search"
          v-model="query"
          type="text"
          placeholder="Enter search query"
        />
        <button type="submit">Search</button>
      </form>
      <ul>
        <li v-for="(result, index) in results" :key="index">{{ result }}</li>
      </ul>
    </div>
  `,
});

// Basic rendering tests
describe('ButtonComponent', () => {
  test('renders button with label', () => {
    render(ButtonComponent, {
      props: { label: 'Click me' },
    });

    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  test('emits click event', async () => {
    const { emitted } = render(ButtonComponent, {
      props: { label: 'Click me' },
    });

    await fireEvent.click(screen.getByText('Click me'));

    expect(emitted().click).toBeTruthy();
    expect(emitted().click).toHaveLength(1);
  });
});

// State testing
describe('CounterComponent', () => {
  test('renders initial count', () => {
    render(CounterComponent);
    expect(screen.getByText('Count: 0')).toBeInTheDocument();
  });

  test('increments count', async () => {
    render(CounterComponent);
    await fireEvent.click(screen.getByText('Increment'));
    expect(screen.getByText('Count: 1')).toBeInTheDocument();
  });

  test('decrements count', async () => {
    render(CounterComponent);
    await fireEvent.click(screen.getByText('Decrement'));
    expect(screen.getByText('Count: -1')).toBeInTheDocument();
  });

  test('resets count', async () => {
    render(CounterComponent);
    await fireEvent.click(screen.getByText('Increment'));
    await fireEvent.click(screen.getByText('Increment'));
    await fireEvent.click(screen.getByText('Reset'));
    expect(screen.getByText('Count: 0')).toBeInTheDocument();
  });
});

// Form testing
describe('SearchComponent', () => {
  test('renders search form', () => {
    render(SearchComponent);
    expect(screen.getByLabelText('Search:')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter search query')).toBeInTheDocument();
  });

  test('updates input value', async () => {
    render(SearchComponent);
    const input = screen.getByLabelText('Search:') as HTMLInputElement;

    await fireEvent.update(input, 'test query');
    expect(input.value).toBe('test query');
  });

  test('submits form and shows results', async () => {
    render(SearchComponent);
    const input = screen.getByLabelText('Search:');
    const submitButton = screen.getByText('Search');

    await fireEvent.update(input, 'vue');
    await fireEvent.click(submitButton);

    expect(screen.getByText('Result for "vue"')).toBeInTheDocument();
  });
});

// User event testing
describe('User Event Tests', () => {
  test('types in input with userEvent', async () => {
    const user = userEvent.setup();
    render(SearchComponent);

    const input = screen.getByLabelText('Search:');
    await user.type(input, 'testing');

    expect(input).toHaveValue('testing');
  });

  test('clicks button with userEvent', async () => {
    const user = userEvent.setup();
    const { emitted } = render(ButtonComponent, {
      props: { label: 'Click me' },
    });

    await user.click(screen.getByText('Click me'));
    expect(emitted().click).toBeTruthy();
  });
});

// Slots testing
const SlotComponent = defineComponent({
  name: 'SlotComponent',
  template: `
    <div>
      <header><slot name="header">Default Header</slot></header>
      <main><slot>Default Content</slot></main>
      <footer><slot name="footer">Default Footer</slot></footer>
    </div>
  `,
});

describe('Slots Testing', () => {
  test('renders default slots', () => {
    render(SlotComponent);
    expect(screen.getByText('Default Header')).toBeInTheDocument();
    expect(screen.getByText('Default Content')).toBeInTheDocument();
  });

  test('renders custom slots', () => {
    render(SlotComponent, {
      slots: {
        header: '<h1>Custom Header</h1>',
        default: '<p>Custom Content</p>',
        footer: '<span>Custom Footer</span>',
      },
    });

    expect(screen.getByText('Custom Header')).toBeInTheDocument();
    expect(screen.getByText('Custom Content')).toBeInTheDocument();
    expect(screen.getByText('Custom Footer')).toBeInTheDocument();
  });
});

// Props validation testing
const PropsComponent = defineComponent({
  name: 'PropsComponent',
  props: {
    title: {
      type: String,
      required: true,
    },
    count: {
      type: Number,
      default: 0,
    },
    isActive: {
      type: Boolean,
      default: false,
    },
  },
  template: `
    <div>
      <h1>{{ title }}</h1>
      <p>Count: {{ count }}</p>
      <p>Active: {{ isActive }}</p>
    </div>
  `,
});

describe('Props Testing', () => {
  test('renders with required props', () => {
    render(PropsComponent, {
      props: { title: 'Test Title' },
    });

    expect(screen.getByText('Test Title')).toBeInTheDocument();
    expect(screen.getByText('Count: 0')).toBeInTheDocument();
  });

  test('renders with all props', () => {
    render(PropsComponent, {
      props: {
        title: 'Custom Title',
        count: 42,
        isActive: true,
      },
    });

    expect(screen.getByText('Custom Title')).toBeInTheDocument();
    expect(screen.getByText('Count: 42')).toBeInTheDocument();
    expect(screen.getByText('Active: true')).toBeInTheDocument();
  });
});

// Async component testing
const AsyncComponent = defineComponent({
  name: 'AsyncComponent',
  setup() {
    const data = ref<string | null>(null);
    const loading = ref(true);

    setTimeout(() => {
      data.value = 'Loaded data';
      loading.value = false;
    }, 100);

    return { data, loading };
  },
  template: `
    <div>
      <p v-if="loading">Loading...</p>
      <p v-else>{{ data }}</p>
    </div>
  `,
});

describe('Async Component Testing', () => {
  test('shows loading state initially', () => {
    render(AsyncComponent);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  test('shows data after loading', async () => {
    render(AsyncComponent);

    await waitFor(() => {
      expect(screen.getByText('Loaded data')).toBeInTheDocument();
    });
  });
});

// Composables testing
describe('Composables Testing', () => {
  const useCounter = () => {
    const count = ref(0);
    const increment = () => count.value++;
    const decrement = () => count.value--;

    return { count, increment, decrement };
  };

  const ComposableComponent = defineComponent({
    name: 'ComposableComponent',
    setup() {
      return useCounter();
    },
    template: `
      <div>
        <p>Count: {{ count }}</p>
        <button @click="increment">+</button>
        <button @click="decrement">-</button>
      </div>
    `,
  });

  test('uses composable correctly', async () => {
    render(ComposableComponent);

    expect(screen.getByText('Count: 0')).toBeInTheDocument();

    await fireEvent.click(screen.getByText('+'));
    expect(screen.getByText('Count: 1')).toBeInTheDocument();

    await fireEvent.click(screen.getByText('-'));
    expect(screen.getByText('Count: 0')).toBeInTheDocument();
  });
});
