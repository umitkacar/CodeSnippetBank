// ErrorMatchers Testing Utilities
// Utility functions for testing

export class ErrorMatchers {
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

describe('ErrorMatchers', () => {
  test('utility function 1', () => {
    expect(ErrorMatchers.utility1()).toBe(true);
  });

  test('utility function 2', () => {
    expect(ErrorMatchers.utility2('test')).toBe('test');
  });

  test('async utility', async () => {
    const result = await ErrorMatchers.asyncUtility();
    expect(result).toBe('result');
  });
});
