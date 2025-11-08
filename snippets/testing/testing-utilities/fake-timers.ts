// FakeTimers Testing Utilities
// Utility functions for testing

export class FakeTimers {
  static utility1() {
    return true;
  }

  static utility2(value: any) {
    return value;
  }

  static async asyncUtility() {
    return Promise.resolve('result');
  }
}

describe('FakeTimers', () => {
  test('utility function 1', () => {
    expect(FakeTimers.utility1()).toBe(true);
  });

  test('utility function 2', () => {
    expect(FakeTimers.utility2('test')).toBe('test');
  });

  test('async utility', async () => {
    const result = await FakeTimers.asyncUtility();
    expect(result).toBe('result');
  });
});
