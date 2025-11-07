// Vitest Advanced Mocking
// Comprehensive mocking patterns for Vitest

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock modules
vi.mock('./api-client', () => ({
  ApiClient: vi.fn().mockImplementation(() => ({
    get: vi.fn().mockResolvedValue({ data: 'mocked' }),
    post: vi.fn().mockResolvedValue({ success: true }),
  })),
}));

describe('Vitest Module Mocking', () => {
  it('mocks entire module', async () => {
    const { ApiClient } = await import('./api-client');
    const client = new ApiClient();
    const result = await client.get('/users');

    expect(result).toEqual({ data: 'mocked' });
  });
});

// Partial module mocking
vi.mock('./user-service', async () => {
  const actual = await vi.importActual<typeof import('./user-service')>('./user-service');
  return {
    ...actual,
    getUser: vi.fn().mockResolvedValue({ id: 1, name: 'Mocked User' }),
  };
});

// Spy on methods
class Calculator {
  add(a: number, b: number): number {
    return a + b;
  }

  multiply(a: number, b: number): number {
    return a * b;
  }
}

describe('Vitest Spies', () => {
  let calc: Calculator;

  beforeEach(() => {
    calc = new Calculator();
  });

  it('spies on method', () => {
    const spy = vi.spyOn(calc, 'add');
    calc.add(2, 3);

    expect(spy).toHaveBeenCalledWith(2, 3);
    expect(spy).toHaveReturnedWith(5);
  });

  it('spies and mocks implementation', () => {
    const spy = vi.spyOn(calc, 'multiply').mockImplementation(() => 100);
    const result = calc.multiply(2, 3);

    expect(result).toBe(100);
    expect(spy).toHaveBeenCalled();
  });
});

// Mock timers
describe('Vitest Timer Mocking', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('advances timers', () => {
    const callback = vi.fn();
    setTimeout(callback, 1000);

    vi.advanceTimersByTime(1000);
    expect(callback).toHaveBeenCalledTimes(1);
  });

  it('runs all timers', () => {
    const callback = vi.fn();
    setTimeout(callback, 1000);
    setTimeout(callback, 2000);

    vi.runAllTimers();
    expect(callback).toHaveBeenCalledTimes(2);
  });

  it('runs only pending timers', () => {
    const callback1 = vi.fn(() => setTimeout(callback2, 1000));
    const callback2 = vi.fn();

    setTimeout(callback1, 1000);
    vi.runOnlyPendingTimers();

    expect(callback1).toHaveBeenCalled();
    expect(callback2).not.toHaveBeenCalled();
  });
});

// Mock dates
describe('Vitest Date Mocking', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('sets system time', () => {
    const date = new Date('2024-01-01');
    vi.setSystemTime(date);

    expect(new Date().toISOString()).toBe(date.toISOString());
  });

  it('advances system time', () => {
    vi.setSystemTime(new Date('2024-01-01'));
    vi.advanceTimersByTime(24 * 60 * 60 * 1000); // 1 day

    expect(new Date().getDate()).toBe(2);
  });
});

// Mock functions with different behaviors
describe('Vitest Mock Behaviors', () => {
  it('mocks sequential return values', () => {
    const mockFn = vi
      .fn()
      .mockReturnValueOnce('first')
      .mockReturnValueOnce('second')
      .mockReturnValue('default');

    expect(mockFn()).toBe('first');
    expect(mockFn()).toBe('second');
    expect(mockFn()).toBe('default');
    expect(mockFn()).toBe('default');
  });

  it('mocks resolved values', async () => {
    const mockFn = vi.fn().mockResolvedValue('success');
    await expect(mockFn()).resolves.toBe('success');
  });

  it('mocks rejected values', async () => {
    const mockFn = vi.fn().mockRejectedValue(new Error('failed'));
    await expect(mockFn()).rejects.toThrow('failed');
  });

  it('mocks sequential async values', async () => {
    const mockFn = vi
      .fn()
      .mockResolvedValueOnce('first')
      .mockResolvedValueOnce('second')
      .mockResolvedValue('default');

    expect(await mockFn()).toBe('first');
    expect(await mockFn()).toBe('second');
    expect(await mockFn()).toBe('default');
  });
});

// Mock implementations
describe('Vitest Mock Implementations', () => {
  it('implements custom logic', () => {
    const mockFn = vi.fn((a: number, b: number) => a * b);
    expect(mockFn(3, 4)).toBe(12);
    expect(mockFn).toHaveBeenCalledWith(3, 4);
  });

  it('implements once', () => {
    const mockFn = vi
      .fn()
      .mockImplementationOnce(() => 'once')
      .mockImplementation(() => 'always');

    expect(mockFn()).toBe('once');
    expect(mockFn()).toBe('always');
    expect(mockFn()).toBe('always');
  });
});
