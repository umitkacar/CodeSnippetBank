// Jest Async Testing Patterns
// Comprehensive async testing examples

class ApiService {
  async fetchUser(id: number): Promise<{ id: number; name: string }> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ id, name: `User ${id}` });
      }, 100);
    });
  }

  async fetchUsers(): Promise<Array<{ id: number; name: string }>> {
    return Promise.all([this.fetchUser(1), this.fetchUser(2), this.fetchUser(3)]);
  }

  async failingRequest(): Promise<never> {
    return new Promise((_, reject) => {
      setTimeout(() => {
        reject(new Error('Request failed'));
      }, 100);
    });
  }
}

describe('Async Testing with Promises', () => {
  const apiService = new ApiService();

  test('async with async/await', async () => {
    const user = await apiService.fetchUser(1);
    expect(user.name).toBe('User 1');
  });

  test('async with return promise', () => {
    return apiService.fetchUser(2).then((user) => {
      expect(user.name).toBe('User 2');
    });
  });

  test('async with resolves matcher', async () => {
    await expect(apiService.fetchUser(3)).resolves.toEqual({
      id: 3,
      name: 'User 3',
    });
  });

  test('async error with rejects matcher', async () => {
    await expect(apiService.failingRequest()).rejects.toThrow('Request failed');
  });

  test('async error with try/catch', async () => {
    try {
      await apiService.failingRequest();
    } catch (error) {
      expect(error).toBeInstanceOf(Error);
      expect((error as Error).message).toBe('Request failed');
    }
  });
});

describe('Async Testing with Multiple Promises', () => {
  const apiService = new ApiService();

  test('Promise.all resolution', async () => {
    const users = await apiService.fetchUsers();
    expect(users).toHaveLength(3);
    expect(users[0].name).toBe('User 1');
  });

  test('concurrent async operations', async () => {
    const [user1, user2] = await Promise.all([
      apiService.fetchUser(1),
      apiService.fetchUser(2),
    ]);

    expect(user1.id).toBe(1);
    expect(user2.id).toBe(2);
  });
});

// Async with timers
describe('Async with Timers', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  test('async with fake timers', () => {
    const callback = jest.fn();

    setTimeout(callback, 1000);
    jest.advanceTimersByTime(1000);

    expect(callback).toHaveBeenCalledTimes(1);
  });

  test('async with runAllTimers', () => {
    const callback = jest.fn();

    setTimeout(callback, 1000);
    setTimeout(callback, 2000);

    jest.runAllTimers();

    expect(callback).toHaveBeenCalledTimes(2);
  });
});

// Async with callbacks
describe('Async with Callbacks', () => {
  test('callback pattern', (done) => {
    function fetchData(callback: (data: string) => void) {
      setTimeout(() => callback('peanut butter'), 100);
    }

    fetchData((data) => {
      expect(data).toBe('peanut butter');
      done();
    });
  });
});
