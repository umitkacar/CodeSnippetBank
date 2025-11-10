// TestDoubles Testing Utilities
// Utility functions for testing

export class TestDoubles {
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

describe('TestDoubles', () => {
  test('utility function 1', () => {
    expect(TestDoubles.utility1()).toBe(true);
  });

  test('utility function 2', () => {
    expect(TestDoubles.utility2('test')).toBe('test');
  });

  test('async utility', async () => {
    const result = await TestDoubles.asyncUtility();
    expect(result).toBe('result');
  });
});
