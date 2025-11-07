// React Testing Library Examples
// Comprehensive RTL testing patterns for React components

import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { useState } from 'react';

// Component examples
function Button({ onClick, children }: { onClick: () => void; children: React.ReactNode }) {
  return <button onClick={onClick}>{children}</button>;
}

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
      <button onClick={() => setCount(count - 1)}>Decrement</button>
      <button onClick={() => setCount(0)}>Reset</button>
    </div>
  );
}

function SearchForm() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<string[]>([]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setResults([`Result for "${query}"`]);
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <label htmlFor="search">Search:</label>
        <input
          id="search"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter search query"
        />
        <button type="submit">Search</button>
      </form>
      <ul>
        {results.map((result, index) => (
          <li key={index}>{result}</li>
        ))}
      </ul>
    </div>
  );
}

// Basic rendering tests
describe('Button Component', () => {
  test('renders button with text', () => {
    render(<Button onClick={() => {}}>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  test('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});

// State testing
describe('Counter Component', () => {
  test('renders initial count', () => {
    render(<Counter />);
    expect(screen.getByText('Count: 0')).toBeInTheDocument();
  });

  test('increments count', () => {
    render(<Counter />);
    fireEvent.click(screen.getByText('Increment'));
    expect(screen.getByText('Count: 1')).toBeInTheDocument();
  });

  test('decrements count', () => {
    render(<Counter />);
    fireEvent.click(screen.getByText('Decrement'));
    expect(screen.getByText('Count: -1')).toBeInTheDocument();
  });

  test('resets count', () => {
    render(<Counter />);
    fireEvent.click(screen.getByText('Increment'));
    fireEvent.click(screen.getByText('Increment'));
    fireEvent.click(screen.getByText('Reset'));
    expect(screen.getByText('Count: 0')).toBeInTheDocument();
  });
});

// Form testing
describe('SearchForm Component', () => {
  test('renders search form', () => {
    render(<SearchForm />);
    expect(screen.getByLabelText('Search:')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter search query')).toBeInTheDocument();
  });

  test('updates input value', () => {
    render(<SearchForm />);
    const input = screen.getByLabelText('Search:') as HTMLInputElement;

    fireEvent.change(input, { target: { value: 'test query' } });
    expect(input.value).toBe('test query');
  });

  test('submits form and shows results', () => {
    render(<SearchForm />);
    const input = screen.getByLabelText('Search:');
    const submitButton = screen.getByText('Search');

    fireEvent.change(input, { target: { value: 'react' } });
    fireEvent.click(submitButton);

    expect(screen.getByText('Result for "react"')).toBeInTheDocument();
  });
});

// User event testing (more realistic)
describe('User Event Tests', () => {
  test('types in input with userEvent', async () => {
    const user = userEvent.setup();
    render(<SearchForm />);

    const input = screen.getByLabelText('Search:');
    await user.type(input, 'testing');

    expect(input).toHaveValue('testing');
  });

  test('clicks button with userEvent', async () => {
    const user = userEvent.setup();
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    await user.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalled();
  });
});

// Queries
describe('Query Examples', () => {
  test('getBy queries', () => {
    render(<Counter />);

    // getByText
    expect(screen.getByText('Count: 0')).toBeInTheDocument();

    // getByRole
    expect(screen.getByRole('button', { name: 'Increment' })).toBeInTheDocument();
  });

  test('queryBy for non-existent elements', () => {
    render(<Counter />);

    // queryBy returns null if not found (doesn't throw)
    expect(screen.queryByText('Not here')).not.toBeInTheDocument();
  });

  test('findBy for async elements', async () => {
    render(<SearchForm />);

    const input = screen.getByLabelText('Search:');
    fireEvent.change(input, { target: { value: 'async' } });
    fireEvent.click(screen.getByText('Search'));

    // findBy waits for element to appear
    const result = await screen.findByText('Result for "async"');
    expect(result).toBeInTheDocument();
  });
});

// Within queries
describe('Within Queries', () => {
  test('scopes queries to container', () => {
    render(
      <div>
        <div data-testid="container1">
          <button>Button 1</button>
        </div>
        <div data-testid="container2">
          <button>Button 2</button>
        </div>
      </div>
    );

    const container1 = screen.getByTestId('container1');
    const button1 = within(container1).getByText('Button 1');

    expect(button1).toBeInTheDocument();
  });
});

// Async testing
describe('Async Tests', () => {
  test('waits for element to appear', async () => {
    function AsyncComponent() {
      const [show, setShow] = useState(false);

      setTimeout(() => setShow(true), 100);

      return <div>{show && <p>Loaded!</p>}</div>;
    }

    render(<AsyncComponent />);

    await waitFor(() => {
      expect(screen.getByText('Loaded!')).toBeInTheDocument();
    });
  });

  test('waits for element to disappear', async () => {
    function DisappearingComponent() {
      const [show, setShow] = useState(true);

      setTimeout(() => setShow(false), 100);

      return <div>{show && <p>Will disappear</p>}</div>;
    }

    render(<DisappearingComponent />);

    await waitFor(() => {
      expect(screen.queryByText('Will disappear')).not.toBeInTheDocument();
    });
  });
});

// Accessibility tests
describe('Accessibility Tests', () => {
  test('has accessible label', () => {
    render(<SearchForm />);
    const input = screen.getByLabelText('Search:');
    expect(input).toHaveAccessibleName('Search:');
  });

  test('buttons have accessible names', () => {
    render(<Counter />);
    expect(screen.getByRole('button', { name: 'Increment' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Decrement' })).toBeInTheDocument();
  });
});

// Custom matchers
describe('Custom Matcher Examples', () => {
  test('uses jest-dom matchers', () => {
    render(<Button onClick={() => {}}>Click me</Button>);
    const button = screen.getByText('Click me');

    expect(button).toBeInTheDocument();
    expect(button).toBeVisible();
    expect(button).toBeEnabled();
    expect(button).toHaveTextContent('Click me');
  });
});
