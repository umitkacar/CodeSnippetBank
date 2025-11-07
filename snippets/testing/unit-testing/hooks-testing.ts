// Test Hooks and Lifecycle
// Comprehensive examples of beforeEach, afterEach, beforeAll, afterAll

describe('Test Hooks and Lifecycle', () => {
  // Basic hooks
  describe('Basic Lifecycle Hooks', () => {
    const logs: string[] = [];

    beforeAll(() => {
      logs.push('beforeAll');
    });

    afterAll(() => {
      logs.push('afterAll');
      // Verify execution order
      expect(logs).toEqual([
        'beforeAll',
        'beforeEach-1',
        'test-1',
        'afterEach-1',
        'beforeEach-2',
        'test-2',
        'afterEach-2',
        'afterAll',
      ]);
    });

    beforeEach(() => {
      logs.push(`beforeEach-${logs.filter((l) => l.startsWith('test')).length + 1}`);
    });

    afterEach(() => {
      logs.push(`afterEach-${logs.filter((l) => l.startsWith('test')).length}`);
    });

    test('first test', () => {
      logs.push('test-1');
      expect(true).toBe(true);
    });

    test('second test', () => {
      logs.push('test-2');
      expect(true).toBe(true);
    });
  });

  // Setup and teardown with state
  describe('State Management in Hooks', () => {
    let counter: number;
    let connection: { connected: boolean };

    beforeEach(() => {
      counter = 0;
      connection = { connected: true };
    });

    afterEach(() => {
      connection.connected = false;
    });

    test('counter starts at 0', () => {
      expect(counter).toBe(0);
    });

    test('counter increments', () => {
      counter++;
      expect(counter).toBe(1);
    });

    test('connection is active', () => {
      expect(connection.connected).toBe(true);
    });
  });

  // Async hooks
  describe('Async Hooks', () => {
    let data: any;

    beforeEach(async () => {
      data = await Promise.resolve({ initialized: true });
    });

    afterEach(async () => {
      await Promise.resolve();
      data = null;
    });

    test('data is initialized', () => {
      expect(data.initialized).toBe(true);
    });

    test('data persists between tests', () => {
      expect(data).toBeDefined();
    });
  });

  // Nested describe blocks
  describe('Nested Hooks', () => {
    const executionOrder: string[] = [];

    beforeAll(() => {
      executionOrder.push('outer beforeAll');
    });

    beforeEach(() => {
      executionOrder.push('outer beforeEach');
    });

    afterEach(() => {
      executionOrder.push('outer afterEach');
    });

    afterAll(() => {
      executionOrder.push('outer afterAll');
    });

    test('outer test', () => {
      executionOrder.push('outer test');
      expect(true).toBe(true);
    });

    describe('Inner suite', () => {
      beforeAll(() => {
        executionOrder.push('inner beforeAll');
      });

      beforeEach(() => {
        executionOrder.push('inner beforeEach');
      });

      afterEach(() => {
        executionOrder.push('inner afterEach');
      });

      afterAll(() => {
        executionOrder.push('inner afterAll');
      });

      test('inner test', () => {
        executionOrder.push('inner test');
        expect(true).toBe(true);
      });
    });
  });

  // Database setup/teardown
  describe('Database Hooks', () => {
    let db: Map<string, any>;

    beforeAll(() => {
      // Initialize database
      db = new Map();
    });

    beforeEach(() => {
      // Seed data
      db.set('user1', { id: 1, name: 'John' });
      db.set('user2', { id: 2, name: 'Jane' });
    });

    afterEach(() => {
      // Clean up data
      db.clear();
    });

    afterAll(() => {
      // Close database connection
      db = null as any;
    });

    test('database has seeded data', () => {
      expect(db.size).toBe(2);
      expect(db.get('user1')).toEqual({ id: 1, name: 'John' });
    });

    test('can add new data', () => {
      db.set('user3', { id: 3, name: 'Bob' });
      expect(db.size).toBe(3);
    });

    test('data is isolated between tests', () => {
      // This test shouldn't see user3 from previous test
      expect(db.size).toBe(2);
    });
  });

  // API client hooks
  describe('API Client Hooks', () => {
    class ApiClient {
      private token: string | null = null;

      setToken(token: string): void {
        this.token = token;
      }

      getToken(): string | null {
        return this.token;
      }

      clearToken(): void {
        this.token = null;
      }
    }

    let client: ApiClient;

    beforeAll(() => {
      client = new ApiClient();
    });

    beforeEach(() => {
      client.setToken('test-token');
    });

    afterEach(() => {
      client.clearToken();
    });

    test('client has token', () => {
      expect(client.getToken()).toBe('test-token');
    });

    test('token is reset for each test', () => {
      client.setToken('different-token');
      expect(client.getToken()).toBe('different-token');
    });
  });

  // Error handling in hooks
  describe('Error Handling in Hooks', () => {
    let setupSuccessful = false;

    beforeEach(() => {
      setupSuccessful = true;
    });

    afterEach(() => {
      // Always runs even if test fails
      setupSuccessful = false;
    });

    test('setup was successful', () => {
      expect(setupSuccessful).toBe(true);
    });

    test('failing test still runs afterEach', () => {
      expect(setupSuccessful).toBe(true);
      // This test will fail but afterEach still runs
    });
  });

  // Conditional hooks
  describe('Conditional Hooks', () => {
    const isIntegrationTest = process.env.INTEGRATION === 'true';
    let externalService: any;

    beforeAll(() => {
      if (isIntegrationTest) {
        externalService = { connected: true };
      }
    });

    beforeEach(() => {
      if (!isIntegrationTest) {
        externalService = { connected: false, mock: true };
      }
    });

    test('service state depends on environment', () => {
      if (isIntegrationTest) {
        expect(externalService.connected).toBe(true);
      } else {
        expect(externalService.mock).toBe(true);
      }
    });
  });

  // Shared setup
  describe('Shared Setup Utility', () => {
    function setupTestEnvironment() {
      const state = {
        users: new Map<number, any>(),
        posts: new Map<number, any>(),
      };

      beforeEach(() => {
        state.users.set(1, { id: 1, name: 'User 1' });
        state.posts.set(1, { id: 1, title: 'Post 1' });
      });

      afterEach(() => {
        state.users.clear();
        state.posts.clear();
      });

      return state;
    }

    const state = setupTestEnvironment();

    test('has users', () => {
      expect(state.users.size).toBe(1);
    });

    test('has posts', () => {
      expect(state.posts.size).toBe(1);
    });
  });

  // Resource cleanup
  describe('Resource Cleanup', () => {
    class Resource {
      private resources: Set<string> = new Set();

      acquire(resource: string): void {
        this.resources.add(resource);
      }

      release(resource: string): void {
        this.resources.delete(resource);
      }

      releaseAll(): void {
        this.resources.clear();
      }

      getResourceCount(): number {
        return this.resources.size;
      }
    }

    let manager: Resource;

    beforeAll(() => {
      manager = new Resource();
    });

    beforeEach(() => {
      manager.acquire('resource1');
      manager.acquire('resource2');
    });

    afterEach(() => {
      manager.releaseAll();
    });

    test('resources are acquired', () => {
      expect(manager.getResourceCount()).toBe(2);
    });

    test('can acquire more resources', () => {
      manager.acquire('resource3');
      expect(manager.getResourceCount()).toBe(3);
    });

    test('resources are cleaned up', () => {
      // Resources from previous test should be cleaned up
      expect(manager.getResourceCount()).toBe(2);
    });
  });

  // Timer hooks
  describe('Timer Hooks', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    test('can fast-forward time', () => {
      const callback = jest.fn();
      setTimeout(callback, 1000);

      jest.advanceTimersByTime(1000);
      expect(callback).toHaveBeenCalled();
    });

    test('timers are reset for each test', () => {
      const callback = jest.fn();
      setTimeout(callback, 1000);

      // Don't advance time
      expect(callback).not.toHaveBeenCalled();
    });
  });

  // Performance measurement
  describe('Performance Hooks', () => {
    let startTime: number;
    let endTime: number;

    beforeEach(() => {
      startTime = Date.now();
    });

    afterEach(() => {
      endTime = Date.now();
      const duration = endTime - startTime;
      // Log or assert performance
      expect(duration).toBeLessThan(1000); // Test should complete in <1s
    });

    test('fast operation', () => {
      // Quick operation
      const result = 1 + 1;
      expect(result).toBe(2);
    });

    test('another fast operation', () => {
      const arr = [1, 2, 3];
      expect(arr).toHaveLength(3);
    });
  });
});
