// Parameterized Testing Patterns
// Comprehensive examples of data-driven testing

describe('Parameterized Testing with test.each', () => {
  // Example 1: Basic parameterized test
  describe('Basic Arithmetic', () => {
    test.each([
      [1, 1, 2],
      [2, 2, 4],
      [3, 5, 8],
      [10, 20, 30],
      [-1, 1, 0],
      [-5, -5, -10],
    ])('adds %i + %i to equal %i', (a, b, expected) => {
      expect(a + b).toBe(expected);
    });

    test.each([
      [10, 2, 5],
      [20, 4, 5],
      [15, 3, 5],
      [100, 10, 10],
    ])('divides %i / %i to equal %i', (a, b, expected) => {
      expect(a / b).toBe(expected);
    });
  });

  // Example 2: String operations
  describe('String Operations', () => {
    test.each([
      ['hello', 'HELLO'],
      ['world', 'WORLD'],
      ['test', 'TEST'],
      ['JavaScript', 'JAVASCRIPT'],
    ])('converts %s to uppercase as %s', (input, expected) => {
      expect(input.toUpperCase()).toBe(expected);
    });

    test.each([
      ['', 0],
      ['a', 1],
      ['hello', 5],
      ['test string', 11],
    ])('string "%s" has length %i', (str, expectedLength) => {
      expect(str.length).toBe(expectedLength);
    });

    test.each([
      ['hello world', 'hello', true],
      ['hello world', 'test', false],
      ['JavaScript', 'Script', true],
      ['testing', 'xyz', false],
    ])('"%s" contains "%s": %s', (str, substring, expected) => {
      expect(str.includes(substring)).toBe(expected);
    });
  });

  // Example 3: Object-based parameters
  describe('Object Parameters', () => {
    test.each([
      { input: 2, multiplier: 3, expected: 6 },
      { input: 5, multiplier: 4, expected: 20 },
      { input: 10, multiplier: 0, expected: 0 },
      { input: -3, multiplier: 2, expected: -6 },
    ])('multiplies $input by $multiplier to get $expected', ({ input, multiplier, expected }) => {
      expect(input * multiplier).toBe(expected);
    });

    test.each([
      { age: 10, category: 'child' },
      { age: 17, category: 'teenager' },
      { age: 25, category: 'adult' },
      { age: 70, category: 'senior' },
    ])('age $age should be categorized as $category', ({ age, category }) => {
      function categorizeAge(age: number): string {
        if (age < 13) return 'child';
        if (age < 20) return 'teenager';
        if (age < 65) return 'adult';
        return 'senior';
      }

      expect(categorizeAge(age)).toBe(category);
    });
  });

  // Example 4: Template literal table
  describe('Template Literal Table', () => {
    test.each`
      a     | b     | expected
      ${1}  | ${1}  | ${2}
      ${1}  | ${2}  | ${3}
      ${2}  | ${1}  | ${3}
      ${5}  | ${10} | ${15}
      ${-5} | ${5}  | ${0}
    `('adds $a + $b to equal $expected', ({ a, b, expected }) => {
      expect(a + b).toBe(expected);
    });

    test.each`
      value    | isEven  | isOdd
      ${2}     | ${true} | ${false}
      ${3}     | ${false} | ${true}
      ${0}     | ${true} | ${false}
      ${-2}    | ${true} | ${false}
      ${-3}    | ${false} | ${true}
    `('$value isEven: $isEven, isOdd: $isOdd', ({ value, isEven, isOdd }) => {
      expect(value % 2 === 0).toBe(isEven);
      expect(value % 2 !== 0).toBe(isOdd);
    });
  });

  // Example 5: Validation tests
  describe('Email Validation', () => {
    test.each([
      ['valid@email.com', true],
      ['user@example.co.uk', true],
      ['test.user@domain.com', true],
      ['invalid.email', false],
      ['@nodomain.com', false],
      ['noat.com', false],
      ['spaces in@email.com', false],
    ])('validates email "%s" as %s', (email, isValid) => {
      function validateEmail(email: string): boolean {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
      }

      expect(validateEmail(email)).toBe(isValid);
    });

    test.each`
      password          | valid    | reason
      ${'short'}        | ${false} | ${'too short'}
      ${'nouppercase1'} | ${false} | ${'no uppercase'}
      ${'NOLOWERCASE1'} | ${false} | ${'no lowercase'}
      ${'NoNumbers'}    | ${false} | ${'no numbers'}
      ${'Valid123'}     | ${true}  | ${'meets all requirements'}
    `('password "$password" is $valid: $reason', ({ password, valid }) => {
      function validatePassword(pwd: string): boolean {
        return (
          pwd.length >= 8 &&
          /[A-Z]/.test(pwd) &&
          /[a-z]/.test(pwd) &&
          /[0-9]/.test(pwd)
        );
      }

      expect(validatePassword(password)).toBe(valid);
    });
  });

  // Example 6: Array operations
  describe('Array Operations', () => {
    test.each([
      [[1, 2, 3], 3],
      [[1, 2, 3, 4, 5], 5],
      [[], 0],
      [[1], 1],
    ])('array %j has length %i', (arr, expectedLength) => {
      expect(arr.length).toBe(expectedLength);
    });

    test.each([
      [[1, 2, 3], 2, true],
      [[1, 2, 3], 5, false],
      [['a', 'b', 'c'], 'b', true],
      [['x', 'y', 'z'], 'w', false],
    ])('array %j contains %s: %s', (arr, element, contains) => {
      expect(arr.includes(element)).toBe(contains);
    });

    test.each`
      array           | filter            | expectedLength
      ${[1, 2, 3, 4]} | ${(x: number) => x > 2} | ${2}
      ${[1, 2, 3, 4]} | ${(x: number) => x % 2 === 0} | ${2}
      ${[1, 2, 3, 4]} | ${(x: number) => x > 10} | ${0}
      ${[1, 2, 3, 4]} | ${(x: number) => x > 0} | ${4}
    `('filtering $array results in $expectedLength items', ({ array, filter, expectedLength }) => {
      expect(array.filter(filter)).toHaveLength(expectedLength);
    });
  });

  // Example 7: HTTP status codes
  describe('HTTP Status Codes', () => {
    test.each`
      code  | message                  | category
      ${200} | ${'OK'}                 | ${'success'}
      ${201} | ${'Created'}            | ${'success'}
      ${400} | ${'Bad Request'}        | ${'client error'}
      ${401} | ${'Unauthorized'}       | ${'client error'}
      ${404} | ${'Not Found'}          | ${'client error'}
      ${500} | ${'Internal Server Error'} | ${'server error'}
      ${503} | ${'Service Unavailable'} | ${'server error'}
    `('$code $message is a $category', ({ code, message, category }) => {
      function categorizeStatus(code: number): string {
        if (code >= 200 && code < 300) return 'success';
        if (code >= 400 && code < 500) return 'client error';
        if (code >= 500 && code < 600) return 'server error';
        return 'unknown';
      }

      expect(categorizeStatus(code)).toBe(category);
    });
  });

  // Example 8: Date operations
  describe('Date Operations', () => {
    test.each([
      ['2024-01-01', '2024-01-02', true],
      ['2024-12-31', '2024-01-01', false],
      ['2024-06-15', '2024-06-15', false],
    ])('%s is before %s: %s', (date1Str, date2Str, isBefore) => {
      const date1 = new Date(date1Str);
      const date2 = new Date(date2Str);
      expect(date1 < date2).toBe(isBefore);
    });

    test.each`
      year   | isLeapYear
      ${2020} | ${true}
      ${2024} | ${true}
      ${2021} | ${false}
      ${2022} | ${false}
      ${2000} | ${true}
      ${1900} | ${false}
    `('$year is leap year: $isLeapYear', ({ year, isLeapYear }) => {
      function isLeap(year: number): boolean {
        return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
      }

      expect(isLeap(year)).toBe(isLeapYear);
    });
  });

  // Example 9: Complex objects
  describe('User Permissions', () => {
    interface User {
      role: string;
      canRead: boolean;
      canWrite: boolean;
      canDelete: boolean;
    }

    test.each<User>([
      { role: 'admin', canRead: true, canWrite: true, canDelete: true },
      { role: 'editor', canRead: true, canWrite: true, canDelete: false },
      { role: 'viewer', canRead: true, canWrite: false, canDelete: false },
      { role: 'guest', canRead: false, canWrite: false, canDelete: false },
    ])('$role permissions', (user) => {
      function checkPermission(user: User, action: string): boolean {
        switch (action) {
          case 'read':
            return user.canRead;
          case 'write':
            return user.canWrite;
          case 'delete':
            return user.canDelete;
          default:
            return false;
        }
      }

      expect(checkPermission(user, 'read')).toBe(user.canRead);
      expect(checkPermission(user, 'write')).toBe(user.canWrite);
      expect(checkPermission(user, 'delete')).toBe(user.canDelete);
    });
  });

  // Example 10: Error cases
  describe('Error Handling', () => {
    test.each([
      [() => JSON.parse('invalid'), SyntaxError],
      [() => { throw new TypeError('type error'); }, TypeError],
      [() => { throw new RangeError('range error'); }, RangeError],
      [() => { throw new Error('generic error'); }, Error],
    ])('handles different error types', (fn, ErrorType) => {
      expect(fn).toThrow(ErrorType);
    });

    test.each`
      value        | errorMessage
      ${null}      | ${'Value cannot be null'}
      ${undefined} | ${'Value cannot be undefined'}
      ${''}        | ${'Value cannot be empty'}
    `('validates value and throws for $value', ({ value, errorMessage }) => {
      function validate(val: any): void {
        if (val === null) throw new Error('Value cannot be null');
        if (val === undefined) throw new Error('Value cannot be undefined');
        if (val === '') throw new Error('Value cannot be empty');
      }

      expect(() => validate(value)).toThrow(errorMessage);
    });
  });
});
