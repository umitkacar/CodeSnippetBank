// Edge Case Testing
// Comprehensive edge case and boundary testing examples

describe('Edge Case Testing', () => {
  // Null and undefined
  describe('Null and Undefined', () => {
    function processValue(value: string | null | undefined): string {
      if (value === null) return 'null';
      if (value === undefined) return 'undefined';
      return value.toUpperCase();
    }

    test('handles null', () => {
      expect(processValue(null)).toBe('null');
    });

    test('handles undefined', () => {
      expect(processValue(undefined)).toBe('undefined');
    });

    test('handles valid string', () => {
      expect(processValue('hello')).toBe('HELLO');
    });
  });

  // Empty collections
  describe('Empty Collections', () => {
    test('empty array', () => {
      const sum = (arr: number[]) => arr.reduce((a, b) => a + b, 0);
      expect(sum([])).toBe(0);
    });

    test('empty string', () => {
      const reverse = (str: string) => str.split('').reverse().join('');
      expect(reverse('')).toBe('');
    });

    test('empty object', () => {
      const keys = (obj: object) => Object.keys(obj);
      expect(keys({})).toEqual([]);
    });

    test('empty map', () => {
      const map = new Map();
      expect(map.size).toBe(0);
      expect(map.get('any')).toBeUndefined();
    });

    test('empty set', () => {
      const set = new Set();
      expect(set.size).toBe(0);
      expect(set.has('any')).toBe(false);
    });
  });

  // Boundary values
  describe('Boundary Values', () => {
    function categorizeAge(age: number): string {
      if (age < 0) return 'invalid';
      if (age < 18) return 'minor';
      if (age < 65) return 'adult';
      return 'senior';
    }

    test('negative age', () => {
      expect(categorizeAge(-1)).toBe('invalid');
    });

    test('zero age', () => {
      expect(categorizeAge(0)).toBe('minor');
    });

    test('just below adult', () => {
      expect(categorizeAge(17)).toBe('minor');
    });

    test('exactly adult boundary', () => {
      expect(categorizeAge(18)).toBe('adult');
    });

    test('just above adult', () => {
      expect(categorizeAge(19)).toBe('adult');
    });

    test('just below senior', () => {
      expect(categorizeAge(64)).toBe('adult');
    });

    test('exactly senior boundary', () => {
      expect(categorizeAge(65)).toBe('senior');
    });

    test('very old age', () => {
      expect(categorizeAge(120)).toBe('senior');
    });
  });

  // Number edge cases
  describe('Number Edge Cases', () => {
    test('maximum safe integer', () => {
      const max = Number.MAX_SAFE_INTEGER;
      expect(max + 1).toBe(max + 1);
      expect(max + 1 === max + 2).toBe(false);
    });

    test('minimum safe integer', () => {
      const min = Number.MIN_SAFE_INTEGER;
      expect(min - 1).toBe(min - 1);
    });

    test('positive infinity', () => {
      expect(1 / 0).toBe(Infinity);
      expect(Infinity + 1).toBe(Infinity);
      expect(Infinity > Number.MAX_VALUE).toBe(true);
    });

    test('negative infinity', () => {
      expect(-1 / 0).toBe(-Infinity);
      expect(-Infinity - 1).toBe(-Infinity);
    });

    test('NaN', () => {
      expect(0 / 0).toBeNaN();
      expect(NaN === NaN).toBe(false);
      expect(Number.isNaN(NaN)).toBe(true);
    });

    test('negative zero', () => {
      expect(-0).toBe(0);
      expect(Object.is(-0, 0)).toBe(false);
      expect(1 / -0).toBe(-Infinity);
    });

    test('floating point precision', () => {
      expect(0.1 + 0.2).not.toBe(0.3);
      expect(0.1 + 0.2).toBeCloseTo(0.3);
    });
  });

  // String edge cases
  describe('String Edge Cases', () => {
    test('very long string', () => {
      const longString = 'a'.repeat(10000);
      expect(longString.length).toBe(10000);
      expect(longString[0]).toBe('a');
      expect(longString[9999]).toBe('a');
    });

    test('special characters', () => {
      const special = '!@#$%^&*()_+-=[]{}|;:,.<>?';
      expect(special.length).toBe(27);
    });

    test('unicode characters', () => {
      const emoji = '👍🎉🚀';
      expect(emoji.length).toBe(6); // Each emoji is 2 code units
      expect([...emoji].length).toBe(3); // Spread gives correct count
    });

    test('whitespace variations', () => {
      const spaces = '   ';
      const tabs = '\t\t\t';
      const newlines = '\n\n\n';
      expect(spaces.trim()).toBe('');
      expect(tabs.trim()).toBe('');
      expect(newlines.trim()).toBe('');
    });

    test('string with null bytes', () => {
      const withNull = 'hello\x00world';
      expect(withNull.length).toBe(11);
      expect(withNull.split('\x00')).toEqual(['hello', 'world']);
    });
  });

  // Array edge cases
  describe('Array Edge Cases', () => {
    test('single element array', () => {
      const arr = [1];
      expect(arr.length).toBe(1);
      expect(arr[0]).toBe(1);
      expect(arr[1]).toBeUndefined();
    });

    test('sparse array', () => {
      const sparse = new Array(5);
      expect(sparse.length).toBe(5);
      expect(sparse[0]).toBeUndefined();
      expect(sparse.filter(() => true)).toEqual([]);
    });

    test('array with holes', () => {
      const arr = [1, , 3]; // Middle element is a hole
      expect(arr.length).toBe(3);
      expect(arr[1]).toBeUndefined();
      expect(1 in arr).toBe(false);
    });

    test('array with mixed types', () => {
      const mixed: any[] = [1, 'two', true, null, undefined, {}, []];
      expect(mixed.length).toBe(7);
      expect(typeof mixed[0]).toBe('number');
      expect(typeof mixed[1]).toBe('string');
      expect(typeof mixed[2]).toBe('boolean');
    });

    test('very large array', () => {
      const large = new Array(1000000).fill(0);
      expect(large.length).toBe(1000000);
      expect(large[0]).toBe(0);
      expect(large[999999]).toBe(0);
    });
  });

  // Object edge cases
  describe('Object Edge Cases', () => {
    test('object with numeric keys', () => {
      const obj: any = { 1: 'one', 2: 'two', 3: 'three' };
      expect(obj[1]).toBe('one');
      expect(obj['1']).toBe('one');
    });

    test('object with symbol keys', () => {
      const sym = Symbol('key');
      const obj = { [sym]: 'value' };
      expect(obj[sym]).toBe('value');
      expect(Object.keys(obj)).toEqual([]);
    });

    test('object with prototype pollution attempt', () => {
      const obj: any = {};
      const maliciousKey = '__proto__';
      obj[maliciousKey] = { polluted: true };

      // Should not pollute prototype
      expect({}.hasOwnProperty('polluted')).toBe(false);
    });

    test('deeply nested object', () => {
      const deep: any = { a: { b: { c: { d: { e: 'value' } } } } };
      expect(deep.a.b.c.d.e).toBe('value');
    });

    test('circular reference', () => {
      const obj: any = { name: 'circular' };
      obj.self = obj;
      expect(obj.self).toBe(obj);
      expect(obj.self.self).toBe(obj);
    });
  });

  // Date edge cases
  describe('Date Edge Cases', () => {
    test('invalid date', () => {
      const invalid = new Date('invalid');
      expect(isNaN(invalid.getTime())).toBe(true);
    });

    test('epoch time', () => {
      const epoch = new Date(0);
      expect(epoch.toISOString()).toBe('1970-01-01T00:00:00.000Z');
    });

    test('very old date', () => {
      const old = new Date('1900-01-01');
      expect(old.getFullYear()).toBe(1900);
    });

    test('far future date', () => {
      const future = new Date('2100-12-31');
      expect(future.getFullYear()).toBe(2100);
    });

    test('date arithmetic edge case', () => {
      const date = new Date('2024-01-31');
      date.setMonth(date.getMonth() + 1); // Add one month
      expect(date.getMonth()).toBe(2); // March (February has fewer days)
    });
  });

  // Division edge cases
  describe('Division Edge Cases', () => {
    function safeDivide(a: number, b: number): number | null {
      if (b === 0) return null;
      return a / b;
    }

    test('divide by zero', () => {
      expect(safeDivide(10, 0)).toBeNull();
    });

    test('divide zero', () => {
      expect(safeDivide(0, 10)).toBe(0);
    });

    test('divide negative by negative', () => {
      expect(safeDivide(-10, -2)).toBe(5);
    });

    test('divide by very small number', () => {
      expect(safeDivide(1, 0.0001)).toBe(10000);
    });
  });

  // Regular expression edge cases
  describe('RegExp Edge Cases', () => {
    test('empty regex', () => {
      const regex = new RegExp('');
      expect(regex.test('anything')).toBe(true);
    });

    test('regex with special characters', () => {
      const regex = /[.*+?^${}()|[\]\\]/;
      expect(regex.test('.')).toBe(true);
      expect(regex.test('a')).toBe(false);
    });

    test('case-insensitive match', () => {
      const regex = /hello/i;
      expect(regex.test('HELLO')).toBe(true);
      expect(regex.test('Hello')).toBe(true);
    });

    test('multiline regex', () => {
      const regex = /^test$/m;
      expect(regex.test('line1\ntest\nline2')).toBe(true);
    });
  });

  // Type coercion edge cases
  describe('Type Coercion', () => {
    test('truthy and falsy values', () => {
      expect(Boolean(0)).toBe(false);
      expect(Boolean('')).toBe(false);
      expect(Boolean(null)).toBe(false);
      expect(Boolean(undefined)).toBe(false);
      expect(Boolean(NaN)).toBe(false);
      expect(Boolean(1)).toBe(true);
      expect(Boolean('0')).toBe(true);
      expect(Boolean([])).toBe(true);
      expect(Boolean({})).toBe(true);
    });

    test('string to number coercion', () => {
      expect(Number('123')).toBe(123);
      expect(Number('12.34')).toBe(12.34);
      expect(Number('0x10')).toBe(16);
      expect(Number('123abc')).toBeNaN();
      expect(Number('')).toBe(0);
    });

    test('implicit coercion', () => {
      expect('5' + 3).toBe('53'); // String concatenation
      expect('5' - 3).toBe(2); // Numeric subtraction
      expect('5' * '2').toBe(10); // Numeric multiplication
    });
  });

  // Concurrency edge cases
  describe('Concurrency Edge Cases', () => {
    test('promise resolution order', async () => {
      const order: number[] = [];

      await Promise.resolve().then(() => order.push(1));
      order.push(2);

      await new Promise((resolve) => {
        order.push(3);
        resolve(null);
      });

      order.push(4);

      expect(order).toEqual([1, 2, 3, 4]);
    });

    test('promise rejection without catch', () => {
      const promise = Promise.reject(new Error('Rejected'));

      // Should not throw in test, but should be handled
      return expect(promise).rejects.toThrow('Rejected');
    });
  });
});
