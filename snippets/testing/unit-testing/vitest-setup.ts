// Vitest Setup and Configuration
// Modern Vite-native test framework examples

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

describe('Vitest Basic Tests', () => {
  it('should perform basic assertions', () => {
    expect(1 + 1).toBe(2);
    expect('hello').toMatch(/hello/);
    expect([1, 2, 3]).toContain(2);
  });

  it('should test objects', () => {
    const user = { name: 'John', age: 30 };
    expect(user).toEqual({ name: 'John', age: 30 });
    expect(user).toHaveProperty('name', 'John');
  });

  it('should test arrays', () => {
    const numbers = [1, 2, 3, 4, 5];
    expect(numbers).toHaveLength(5);
    expect(numbers).toContain(3);
    expect(numbers).toEqual(expect.arrayContaining([2, 4]));
  });
});

describe('Vitest Matchers', () => {
  it('truthiness matchers', () => {
    expect(true).toBeTruthy();
    expect(false).toBeFalsy();
    expect(null).toBeNull();
    expect(undefined).toBeUndefined();
    expect('hello').toBeDefined();
  });

  it('number matchers', () => {
    expect(10).toBeGreaterThan(5);
    expect(5).toBeLessThan(10);
    expect(10).toBeGreaterThanOrEqual(10);
    expect(5).toBeLessThanOrEqual(5);
    expect(0.1 + 0.2).toBeCloseTo(0.3);
  });

  it('string matchers', () => {
    expect('hello world').toMatch(/world/);
    expect('hello').toContain('ell');
    expect('HELLO').not.toBe('hello');
  });
});

describe('Vitest Lifecycle Hooks', () => {
  let count = 0;

  beforeEach(() => {
    count = 0;
  });

  afterEach(() => {
    count = 0;
  });

  it('increments count', () => {
    count++;
    expect(count).toBe(1);
  });

  it('starts with count at 0', () => {
    expect(count).toBe(0);
  });
});

// Async testing with Vitest
describe('Vitest Async Tests', () => {
  it('resolves promise', async () => {
    const data = await Promise.resolve('success');
    expect(data).toBe('success');
  });

  it('rejects promise', async () => {
    await expect(Promise.reject(new Error('fail'))).rejects.toThrow('fail');
  });

  it('async with timeout', async () => {
    const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));
    await delay(100);
    expect(true).toBe(true);
  }, 200);
});

// Mock functions with Vitest
describe('Vitest Mocking', () => {
  it('creates mock function', () => {
    const mockFn = vi.fn((x: number) => x * 2);
    mockFn(5);

    expect(mockFn).toHaveBeenCalledWith(5);
    expect(mockFn).toHaveReturnedWith(10);
  });

  it('mocks return values', () => {
    const mockFn = vi.fn();
    mockFn.mockReturnValue('mocked');

    expect(mockFn()).toBe('mocked');
  });

  it('mocks implementation', () => {
    const mockFn = vi.fn().mockImplementation((a: number, b: number) => a + b);
    expect(mockFn(1, 2)).toBe(3);
  });
});
