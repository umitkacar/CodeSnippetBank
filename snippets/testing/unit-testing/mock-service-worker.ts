// Mock Service Worker (MSW) Examples
// API mocking for testing and development

import { rest } from 'msw';
import { setupServer } from 'msw/node';

// Define API handlers
const handlers = [
  // GET request handler
  rest.get('https://api.example.com/users', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        { id: 1, name: 'John Doe', email: 'john@example.com' },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com' },
      ])
    );
  }),

  // GET single user
  rest.get('https://api.example.com/users/:id', (req, res, ctx) => {
    const { id } = req.params;
    return res(
      ctx.status(200),
      ctx.json({
        id: Number(id),
        name: 'John Doe',
        email: 'john@example.com',
      })
    );
  }),

  // POST request handler
  rest.post('https://api.example.com/users', async (req, res, ctx) => {
    const body = await req.json();
    return res(
      ctx.status(201),
      ctx.json({
        id: 3,
        ...body,
      })
    );
  }),

  // PUT request handler
  rest.put('https://api.example.com/users/:id', async (req, res, ctx) => {
    const { id } = req.params;
    const body = await req.json();
    return res(
      ctx.status(200),
      ctx.json({
        id: Number(id),
        ...body,
      })
    );
  }),

  // DELETE request handler
  rest.delete('https://api.example.com/users/:id', (req, res, ctx) => {
    return res(ctx.status(204));
  }),

  // Error response
  rest.get('https://api.example.com/error', (req, res, ctx) => {
    return res(
      ctx.status(500),
      ctx.json({ error: 'Internal Server Error' })
    );
  }),

  // Delayed response
  rest.get('https://api.example.com/slow', (req, res, ctx) => {
    return res(
      ctx.delay(1000),
      ctx.status(200),
      ctx.json({ message: 'Slow response' })
    );
  }),

  // Conditional response
  rest.get('https://api.example.com/conditional', (req, res, ctx) => {
    const auth = req.headers.get('Authorization');

    if (!auth) {
      return res(ctx.status(401), ctx.json({ error: 'Unauthorized' }));
    }

    return res(ctx.status(200), ctx.json({ message: 'Authorized' }));
  }),

  // Query parameters
  rest.get('https://api.example.com/search', (req, res, ctx) => {
    const query = req.url.searchParams.get('q');
    const limit = req.url.searchParams.get('limit');

    return res(
      ctx.status(200),
      ctx.json({
        query,
        limit: limit ? Number(limit) : 10,
        results: [`Result for ${query}`],
      })
    );
  }),
];

// Setup server
const server = setupServer(...handlers);

// Test setup
describe('MSW API Mocking', () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  test('fetches users list', async () => {
    const response = await fetch('https://api.example.com/users');
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data).toHaveLength(2);
    expect(data[0].name).toBe('John Doe');
  });

  test('fetches single user', async () => {
    const response = await fetch('https://api.example.com/users/1');
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.id).toBe(1);
    expect(data.name).toBe('John Doe');
  });

  test('creates new user', async () => {
    const response = await fetch('https://api.example.com/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: 'New User', email: 'new@example.com' }),
    });
    const data = await response.json();

    expect(response.status).toBe(201);
    expect(data.id).toBe(3);
    expect(data.name).toBe('New User');
  });

  test('updates user', async () => {
    const response = await fetch('https://api.example.com/users/1', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: 'Updated User' }),
    });
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.name).toBe('Updated User');
  });

  test('deletes user', async () => {
    const response = await fetch('https://api.example.com/users/1', {
      method: 'DELETE',
    });

    expect(response.status).toBe(204);
  });

  test('handles error response', async () => {
    const response = await fetch('https://api.example.com/error');
    const data = await response.json();

    expect(response.status).toBe(500);
    expect(data.error).toBe('Internal Server Error');
  });

  test('handles conditional response', async () => {
    const response = await fetch('https://api.example.com/conditional', {
      headers: { Authorization: 'Bearer token' },
    });

    expect(response.status).toBe(200);
  });

  test('handles unauthorized request', async () => {
    const response = await fetch('https://api.example.com/conditional');
    expect(response.status).toBe(401);
  });

  test('handles query parameters', async () => {
    const response = await fetch(
      'https://api.example.com/search?q=test&limit=5'
    );
    const data = await response.json();

    expect(data.query).toBe('test');
    expect(data.limit).toBe(5);
  });

  // Runtime handler override
  test('overrides handler at runtime', async () => {
    server.use(
      rest.get('https://api.example.com/users', (req, res, ctx) => {
        return res(ctx.status(200), ctx.json([]));
      })
    );

    const response = await fetch('https://api.example.com/users');
    const data = await response.json();

    expect(data).toHaveLength(0);
  });
});

// Advanced MSW patterns
describe('Advanced MSW Patterns', () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  test('simulates network error', async () => {
    server.use(
      rest.get('https://api.example.com/users', (req, res) => {
        return res.networkError('Failed to connect');
      })
    );

    await expect(fetch('https://api.example.com/users')).rejects.toThrow();
  });

  test('simulates timeout', async () => {
    server.use(
      rest.get('https://api.example.com/users', (req, res, ctx) => {
        return res(ctx.delay('infinite'));
      })
    );

    // Test with timeout would go here
  });

  test('sequences responses', async () => {
    server.use(
      rest.get(
        'https://api.example.com/sequence',
        (req, res, ctx) => res.once(ctx.status(200), ctx.json({ attempt: 1 })),
        (req, res, ctx) => res.once(ctx.status(200), ctx.json({ attempt: 2 })),
        (req, res, ctx) => res(ctx.status(200), ctx.json({ attempt: 3 }))
      )
    );

    const response1 = await fetch('https://api.example.com/sequence');
    const data1 = await response1.json();
    expect(data1.attempt).toBe(1);

    const response2 = await fetch('https://api.example.com/sequence');
    const data2 = await response2.json();
    expect(data2.attempt).toBe(2);

    const response3 = await fetch('https://api.example.com/sequence');
    const data3 = await response3.json();
    expect(data3.attempt).toBe(3);
  });
});
