// Jest Coverage Configuration and Optimization
// Comprehensive coverage examples and best practices

// jest.config.js example configuration
export const coverageConfig = {
  // Coverage collection
  collectCoverage: true,
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{js,jsx,ts,tsx}',
    '!src/**/__tests__/**',
    '!src/**/__mocks__/**',
    '!src/index.{js,ts}',
  ],

  // Coverage thresholds
  coverageThresholds: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
    './src/components/': {
      branches: 90,
      functions: 90,
      lines: 90,
      statements: 90,
    },
  },

  // Coverage reporters
  coverageReporters: ['text', 'text-summary', 'html', 'lcov', 'json'],

  // Coverage directory
  coverageDirectory: 'coverage',
};

// Example class with full coverage
export class MathOperations {
  add(a: number, b: number): number {
    return a + b;
  }

  subtract(a: number, b: number): number {
    return a - b;
  }

  multiply(a: number, b: number): number {
    return a * b;
  }

  divide(a: number, b: number): number {
    if (b === 0) {
      throw new Error('Division by zero');
    }
    return a / b;
  }

  modulo(a: number, b: number): number {
    if (b === 0) {
      throw new Error('Modulo by zero');
    }
    return a % b;
  }

  power(base: number, exponent: number): number {
    return Math.pow(base, exponent);
  }

  isEven(n: number): boolean {
    return n % 2 === 0;
  }

  isOdd(n: number): boolean {
    return n % 2 !== 0;
  }

  absolute(n: number): number {
    return Math.abs(n);
  }
}

// Comprehensive tests for 100% coverage
describe('MathOperations - Full Coverage', () => {
  let math: MathOperations;

  beforeEach(() => {
    math = new MathOperations();
  });

  describe('add', () => {
    test('adds positive numbers', () => {
      expect(math.add(2, 3)).toBe(5);
    });

    test('adds negative numbers', () => {
      expect(math.add(-2, -3)).toBe(-5);
    });

    test('adds mixed numbers', () => {
      expect(math.add(-2, 3)).toBe(1);
    });
  });

  describe('subtract', () => {
    test('subtracts positive numbers', () => {
      expect(math.subtract(5, 3)).toBe(2);
    });

    test('subtracts negative numbers', () => {
      expect(math.subtract(-5, -3)).toBe(-2);
    });
  });

  describe('multiply', () => {
    test('multiplies positive numbers', () => {
      expect(math.multiply(3, 4)).toBe(12);
    });

    test('multiplies by zero', () => {
      expect(math.multiply(5, 0)).toBe(0);
    });

    test('multiplies negative numbers', () => {
      expect(math.multiply(-3, -4)).toBe(12);
    });
  });

  describe('divide', () => {
    test('divides positive numbers', () => {
      expect(math.divide(10, 2)).toBe(5);
    });

    test('throws on division by zero', () => {
      expect(() => math.divide(10, 0)).toThrow('Division by zero');
    });

    test('divides negative numbers', () => {
      expect(math.divide(-10, 2)).toBe(-5);
    });
  });

  describe('modulo', () => {
    test('calculates modulo', () => {
      expect(math.modulo(10, 3)).toBe(1);
    });

    test('throws on modulo by zero', () => {
      expect(() => math.modulo(10, 0)).toThrow('Modulo by zero');
    });
  });

  describe('power', () => {
    test('calculates power', () => {
      expect(math.power(2, 3)).toBe(8);
    });

    test('calculates zero power', () => {
      expect(math.power(5, 0)).toBe(1);
    });
  });

  describe('isEven', () => {
    test('identifies even numbers', () => {
      expect(math.isEven(4)).toBe(true);
      expect(math.isEven(0)).toBe(true);
    });

    test('identifies odd numbers', () => {
      expect(math.isEven(3)).toBe(false);
    });
  });

  describe('isOdd', () => {
    test('identifies odd numbers', () => {
      expect(math.isOdd(3)).toBe(true);
      expect(math.isOdd(-3)).toBe(true);
    });

    test('identifies even numbers', () => {
      expect(math.isOdd(4)).toBe(false);
    });
  });

  describe('absolute', () => {
    test('returns absolute value of positive number', () => {
      expect(math.absolute(5)).toBe(5);
    });

    test('returns absolute value of negative number', () => {
      expect(math.absolute(-5)).toBe(5);
    });

    test('returns zero', () => {
      expect(math.absolute(0)).toBe(0);
    });
  });
});

// Example with branch coverage
export class UserValidator {
  validateAge(age: number): string {
    if (age < 0) {
      return 'Invalid age';
    } else if (age < 18) {
      return 'Minor';
    } else if (age < 65) {
      return 'Adult';
    } else {
      return 'Senior';
    }
  }

  validateEmail(email: string): boolean {
    if (!email) {
      return false;
    }
    if (!email.includes('@')) {
      return false;
    }
    if (!email.includes('.')) {
      return false;
    }
    return true;
  }

  validatePassword(password: string): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (password.length < 8) {
      errors.push('Password must be at least 8 characters');
    }
    if (!/[A-Z]/.test(password)) {
      errors.push('Password must contain uppercase letter');
    }
    if (!/[a-z]/.test(password)) {
      errors.push('Password must contain lowercase letter');
    }
    if (!/[0-9]/.test(password)) {
      errors.push('Password must contain number');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }
}

// Tests covering all branches
describe('UserValidator - Branch Coverage', () => {
  let validator: UserValidator;

  beforeEach(() => {
    validator = new UserValidator();
  });

  describe('validateAge', () => {
    test('validates invalid age', () => {
      expect(validator.validateAge(-1)).toBe('Invalid age');
    });

    test('validates minor', () => {
      expect(validator.validateAge(10)).toBe('Minor');
    });

    test('validates adult', () => {
      expect(validator.validateAge(30)).toBe('Adult');
    });

    test('validates senior', () => {
      expect(validator.validateAge(70)).toBe('Senior');
    });

    test('validates boundary cases', () => {
      expect(validator.validateAge(0)).toBe('Minor');
      expect(validator.validateAge(18)).toBe('Adult');
      expect(validator.validateAge(65)).toBe('Senior');
    });
  });

  describe('validateEmail', () => {
    test('validates empty email', () => {
      expect(validator.validateEmail('')).toBe(false);
    });

    test('validates email without @', () => {
      expect(validator.validateEmail('invalid.email')).toBe(false);
    });

    test('validates email without dot', () => {
      expect(validator.validateEmail('invalid@email')).toBe(false);
    });

    test('validates correct email', () => {
      expect(validator.validateEmail('valid@email.com')).toBe(true);
    });
  });

  describe('validatePassword', () => {
    test('validates short password', () => {
      const result = validator.validatePassword('Short1');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Password must be at least 8 characters');
    });

    test('validates password without uppercase', () => {
      const result = validator.validatePassword('password123');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Password must contain uppercase letter');
    });

    test('validates password without lowercase', () => {
      const result = validator.validatePassword('PASSWORD123');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Password must contain lowercase letter');
    });

    test('validates password without number', () => {
      const result = validator.validatePassword('Password');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Password must contain number');
    });

    test('validates correct password', () => {
      const result = validator.validatePassword('Password123');
      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });
  });
});
