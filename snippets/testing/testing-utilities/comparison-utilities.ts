// ComparisonUtilities Testing Utilities
// Utility functions for testing

export class ComparisonUtilities {
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

describe('ComparisonUtilities', () => {
  test('utility function 1', () => {
    expect(ComparisonUtilities.utility1()).toBe(true);
  });

  test('utility function 2', () => {
    expect(ComparisonUtilities.utility2('test')).toBe('test');
  });

  test('async utility', async () => {
    const result = await ComparisonUtilities.asyncUtility();
    expect(result).toBe('result');
  });
});
