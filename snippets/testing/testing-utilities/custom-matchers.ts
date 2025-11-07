// Custom Jest Matchers
// Extend Jest with custom assertion matchers

export const customMatchers = {
  toBeValidEmail(received: string) {
    const pass = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(received);
    return {
      pass,
      message: () =>
        pass
          ? `expected ${received} not to be a valid email`
          : `expected ${received} to be a valid email`,
    };
  },

  toBeWithinRange(received: number, floor: number, ceiling: number) {
    const pass = received >= floor && received <= ceiling;
    return {
      pass,
      message: () =>
        pass
          ? `expected ${received} not to be within range ${floor} - ${ceiling}`
          : `expected ${received} to be within range ${floor} - ${ceiling}`,
    };
  },

  toHaveStatus(received: any, expected: number) {
    const pass = received.status === expected;
    return {
      pass,
      message: () =>
        pass
          ? `expected status not to be ${expected}`
          : `expected status to be ${expected}, got ${received.status}`,
    };
  },
};

declare global {
  namespace jest {
    interface Matchers<R> {
      toBeValidEmail(): R;
      toBeWithinRange(floor: number, ceiling: number): R;
      toHaveStatus(status: number): R;
    }
  }
}

describe('Custom Matchers', () => {
  beforeAll(() => {
    expect.extend(customMatchers);
  });

  test('validates email', () => {
    expect('test@example.com').toBeValidEmail();
    expect('invalid').not.toBeValidEmail();
  });

  test('checks range', () => {
    expect(5).toBeWithinRange(1, 10);
    expect(15).not.toBeWithinRange(1, 10);
  });

  test('checks status', () => {
    expect({ status: 200 }).toHaveStatus(200);
  });
});
