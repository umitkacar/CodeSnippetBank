/**
 * Next.js Testing patterns
 */

// Jest configuration - jest.config.js
const nextJest = require('next/jest');

const createJestConfig = nextJest({
  dir: './',
});

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
  collectCoverageFrom: [
    'app/**/*.{js,jsx,ts,tsx}',
    'components/**/*.{js,jsx,ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
  ],
};

module.exports = createJestConfig(customJestConfig);

// jest.setup.js
import '@testing-library/jest-dom';

// Component testing with React Testing Library
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from './Button';

describe('Button', () => {
  it('renders button with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', async () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    await userEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('disables button when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>);
    expect(screen.getByText('Click me')).toBeDisabled();
  });
});

// Server Component testing
import { GET } from '@/app/api/users/route';

describe('Users API', () => {
  it('returns users list', async () => {
    const req = new Request('http://localhost:3000/api/users');
    const response = await GET(req);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(Array.isArray(data)).toBe(true);
  });
});

// Server Action testing
import { createPost } from '@/app/actions';

describe('createPost', () => {
  it('creates a new post', async () => {
    const formData = new FormData();
    formData.append('title', 'Test Post');
    formData.append('content', 'Test content');

    const result = await createPost(formData);
    expect(result.success).toBe(true);
  });

  it('validates required fields', async () => {
    const formData = new FormData();
    const result = await createPost(formData);
    expect(result.error).toBeDefined();
  });
});

// E2E testing with Playwright
import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test('should navigate to products page', async ({ page }) => {
    await page.goto('/');
    await page.click('text=Products');
    await expect(page).toHaveURL('/products');
  });

  test('should display product list', async ({ page }) => {
    await page.goto('/products');
    const products = page.locator('[data-testid="product-card"]');
    await expect(products).toHaveCount(10);
  });
});

// Mock Next.js router
import { useRouter } from 'next/navigation';

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  usePathname: jest.fn(),
  useSearchParams: jest.fn(),
}));

describe('Navigation Component', () => {
  it('navigates on button click', () => {
    const push = jest.fn();
    (useRouter as jest.Mock).mockReturnValue({ push });

    render(<NavigationComponent />);
    fireEvent.click(screen.getByText('Go to Products'));

    expect(push).toHaveBeenCalledWith('/products');
  });
});

// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve({ data: 'mocked data' }),
    ok: true,
  })
) as jest.Mock;

describe('Data Fetching', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('fetches data successfully', async () => {
    const data = await fetchData();
    expect(data).toEqual({ data: 'mocked data' });
    expect(fetch).toHaveBeenCalledWith('https://api.example.com/data');
  });
});

// Testing with MSW (Mock Service Worker)
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.get('/api/users', (req, res, ctx) => {
    return res(
      ctx.json([
        { id: '1', name: 'John' },
        { id: '2', name: 'Jane' },
      ])
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Users API with MSW', () => {
  it('fetches users', async () => {
    const response = await fetch('/api/users');
    const data = await response.json();

    expect(data).toHaveLength(2);
    expect(data[0].name).toBe('John');
  });
});

// Snapshot testing
import renderer from 'react-test-renderer';

describe('Component Snapshot', () => {
  it('matches snapshot', () => {
    const tree = renderer.create(<MyComponent />).toJSON();
    expect(tree).toMatchSnapshot();
  });
});

// Helper functions
function NavigationComponent() {
  const router = useRouter();
  return (
    <button onClick={() => router.push('/products')}>Go to Products</button>
  );
}

async function fetchData() {
  const response = await fetch('https://api.example.com/data');
  return response.json();
}

function MyComponent() {
  return <div>My Component</div>;
}

import { fireEvent } from '@testing-library/react';
