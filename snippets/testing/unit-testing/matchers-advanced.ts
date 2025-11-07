// Advanced Jest Matchers
// Comprehensive matcher examples for assertions

describe('Advanced Jest Matchers', () => {
  // Equality matchers
  describe('Equality Matchers', () => {
    test('toBe for primitive equality', () => {
      expect(2 + 2).toBe(4);
      expect('hello').toBe('hello');
      expect(true).toBe(true);
    });

    test('toEqual for deep equality', () => {
      expect({ a: 1, b: 2 }).toEqual({ a: 1, b: 2 });
      expect([1, 2, 3]).toEqual([1, 2, 3]);
    });

    test('toStrictEqual for strict equality', () => {
      expect({ a: undefined }).not.toEqual({ b: 2 });
      expect({ a: 1 }).toStrictEqual({ a: 1 });
    });

    test('not modifier', () => {
      expect(5).not.toBe(6);
      expect('hello').not.toBe('world');
    });
  });

  // Truthiness matchers
  describe('Truthiness Matchers', () => {
    test('toBeTruthy', () => {
      expect(true).toBeTruthy();
      expect(1).toBeTruthy();
      expect('hello').toBeTruthy();
      expect({}).toBeTruthy();
    });

    test('toBeFalsy', () => {
      expect(false).toBeFalsy();
      expect(0).toBeFalsy();
      expect('').toBeFalsy();
      expect(null).toBeFalsy();
      expect(undefined).toBeFalsy();
    });

    test('toBeNull', () => {
      expect(null).toBeNull();
      expect(undefined).not.toBeNull();
    });

    test('toBeUndefined', () => {
      expect(undefined).toBeUndefined();
      expect(null).not.toBeUndefined();
    });

    test('toBeDefined', () => {
      expect(0).toBeDefined();
      expect('').toBeDefined();
      expect(null).toBeDefined();
      expect(undefined).not.toBeDefined();
    });
  });

  // Number matchers
  describe('Number Matchers', () => {
    test('toBeGreaterThan', () => {
      expect(10).toBeGreaterThan(5);
      expect(0).toBeGreaterThan(-1);
    });

    test('toBeGreaterThanOrEqual', () => {
      expect(10).toBeGreaterThanOrEqual(10);
      expect(11).toBeGreaterThanOrEqual(10);
    });

    test('toBeLessThan', () => {
      expect(5).toBeLessThan(10);
      expect(-1).toBeLessThan(0);
    });

    test('toBeLessThanOrEqual', () => {
      expect(10).toBeLessThanOrEqual(10);
      expect(9).toBeLessThanOrEqual(10);
    });

    test('toBeCloseTo for floating point', () => {
      expect(0.1 + 0.2).toBeCloseTo(0.3);
      expect(0.1 + 0.2).not.toBe(0.3); // Floating point precision
    });

    test('toBeNaN', () => {
      expect(NaN).toBeNaN();
      expect(0 / 0).toBeNaN();
      expect(parseInt('invalid')).toBeNaN();
    });
  });

  // String matchers
  describe('String Matchers', () => {
    test('toMatch with regex', () => {
      expect('hello world').toMatch(/world/);
      expect('test@example.com').toMatch(/\w+@\w+\.\w+/);
    });

    test('toMatch with string', () => {
      expect('hello world').toMatch('world');
      expect('JavaScript').toMatch('Script');
    });

    test('toContain for strings', () => {
      expect('hello world').toContain('world');
      expect('JavaScript').toContain('Java');
    });

    test('string length', () => {
      expect('hello').toHaveLength(5);
      expect('').toHaveLength(0);
    });
  });

  // Array matchers
  describe('Array Matchers', () => {
    test('toContain for arrays', () => {
      expect([1, 2, 3, 4]).toContain(3);
      expect(['a', 'b', 'c']).toContain('b');
    });

    test('toHaveLength', () => {
      expect([1, 2, 3]).toHaveLength(3);
      expect([]).toHaveLength(0);
    });

    test('toContainEqual for objects', () => {
      const users = [{ id: 1 }, { id: 2 }];
      expect(users).toContainEqual({ id: 1 });
    });

    test('arrayContaining', () => {
      expect([1, 2, 3, 4, 5]).toEqual(expect.arrayContaining([2, 4]));
      expect([1, 2, 3]).toEqual(expect.arrayContaining([1, 3]));
    });
  });

  // Object matchers
  describe('Object Matchers', () => {
    test('toHaveProperty', () => {
      const user = { id: 1, name: 'John', email: 'john@example.com' };
      expect(user).toHaveProperty('id');
      expect(user).toHaveProperty('name', 'John');
      expect(user).toHaveProperty('email');
    });

    test('toHaveProperty with nested path', () => {
      const obj = { user: { profile: { name: 'John' } } };
      expect(obj).toHaveProperty('user.profile.name');
      expect(obj).toHaveProperty('user.profile.name', 'John');
    });

    test('toMatchObject', () => {
      const user = { id: 1, name: 'John', email: 'john@example.com' };
      expect(user).toMatchObject({ name: 'John' });
      expect(user).toMatchObject({ id: 1, name: 'John' });
    });

    test('objectContaining', () => {
      const user = { id: 1, name: 'John', email: 'john@example.com' };
      expect(user).toEqual(expect.objectContaining({ id: 1 }));
      expect(user).toEqual(expect.objectContaining({ name: 'John', email: 'john@example.com' }));
    });
  });

  // Type matchers
  describe('Type Matchers', () => {
    test('expect.any', () => {
      expect({ id: 1, name: 'John' }).toEqual({
        id: expect.any(Number),
        name: expect.any(String),
      });
    });

    test('expect.anything', () => {
      expect('hello').toEqual(expect.anything());
      expect(123).toEqual(expect.anything());
      expect(null).not.toEqual(expect.anything());
      expect(undefined).not.toEqual(expect.anything());
    });

    test('toBeInstanceOf', () => {
      expect(new Date()).toBeInstanceOf(Date);
      expect([]).toBeInstanceOf(Array);
      expect({}).toBeInstanceOf(Object);
    });
  });

  // Error matchers
  describe('Error Matchers', () => {
    test('toThrow', () => {
      expect(() => {
        throw new Error('error');
      }).toThrow();
    });

    test('toThrow with message', () => {
      expect(() => {
        throw new Error('specific error');
      }).toThrow('specific error');
    });

    test('toThrow with regex', () => {
      expect(() => {
        throw new Error('Error: 404');
      }).toThrow(/404/);
    });

    test('toThrow with error type', () => {
      expect(() => {
        throw new TypeError('type error');
      }).toThrow(TypeError);
    });

    test('toThrowErrorMatchingSnapshot', () => {
      expect(() => {
        throw new Error('snapshot error');
      }).toThrowErrorMatchingSnapshot();
    });
  });

  // Promise matchers
  describe('Promise Matchers', () => {
    test('resolves', async () => {
      await expect(Promise.resolve('success')).resolves.toBe('success');
    });

    test('rejects', async () => {
      await expect(Promise.reject('error')).rejects.toBe('error');
    });

    test('resolves with object', async () => {
      await expect(Promise.resolve({ status: 'ok' })).resolves.toEqual({ status: 'ok' });
    });

    test('rejects with error', async () => {
      await expect(Promise.reject(new Error('failed'))).rejects.toThrow('failed');
    });
  });

  // Mock function matchers
  describe('Mock Function Matchers', () => {
    test('toHaveBeenCalled', () => {
      const mock = jest.fn();
      mock();
      expect(mock).toHaveBeenCalled();
    });

    test('toHaveBeenCalledTimes', () => {
      const mock = jest.fn();
      mock();
      mock();
      expect(mock).toHaveBeenCalledTimes(2);
    });

    test('toHaveBeenCalledWith', () => {
      const mock = jest.fn();
      mock(1, 2, 3);
      expect(mock).toHaveBeenCalledWith(1, 2, 3);
    });

    test('toHaveBeenLastCalledWith', () => {
      const mock = jest.fn();
      mock(1, 2);
      mock(3, 4);
      expect(mock).toHaveBeenLastCalledWith(3, 4);
    });

    test('toHaveBeenNthCalledWith', () => {
      const mock = jest.fn();
      mock('first');
      mock('second');
      mock('third');
      expect(mock).toHaveBeenNthCalledWith(1, 'first');
      expect(mock).toHaveBeenNthCalledWith(2, 'second');
    });

    test('toHaveReturned', () => {
      const mock = jest.fn(() => 'value');
      mock();
      expect(mock).toHaveReturned();
    });

    test('toHaveReturnedTimes', () => {
      const mock = jest.fn(() => 'value');
      mock();
      mock();
      expect(mock).toHaveReturnedTimes(2);
    });

    test('toHaveReturnedWith', () => {
      const mock = jest.fn(() => 42);
      mock();
      expect(mock).toHaveReturnedWith(42);
    });

    test('toHaveLastReturnedWith', () => {
      const mock = jest.fn();
      mock.mockReturnValueOnce(1);
      mock.mockReturnValueOnce(2);
      mock();
      mock();
      expect(mock).toHaveLastReturnedWith(2);
    });
  });

  // Snapshot matchers
  describe('Snapshot Matchers', () => {
    test('toMatchSnapshot', () => {
      const data = { id: 1, name: 'John', created: new Date('2024-01-01') };
      expect(data).toMatchSnapshot({
        created: expect.any(Date),
      });
    });

    test('toMatchInlineSnapshot', () => {
      expect({ foo: 'bar' }).toMatchInlineSnapshot(`
        {
          "foo": "bar",
        }
      `);
    });
  });

  // Custom matchers
  describe('Custom Matchers', () => {
    expect.extend({
      toBeWithinRange(received: number, floor: number, ceiling: number) {
        const pass = received >= floor && received <= ceiling;
        if (pass) {
          return {
            message: () =>
              `expected ${received} not to be within range ${floor} - ${ceiling}`,
            pass: true,
          };
        } else {
          return {
            message: () =>
              `expected ${received} to be within range ${floor} - ${ceiling}`,
            pass: false,
          };
        }
      },
    });

    test('uses custom matcher', () => {
      expect(15).toBeWithinRange(10, 20);
      expect(5).not.toBeWithinRange(10, 20);
    });
  });

  // Asymmetric matchers
  describe('Asymmetric Matchers', () => {
    test('stringContaining', () => {
      expect('hello world').toEqual(expect.stringContaining('world'));
    });

    test('stringMatching', () => {
      expect('test@example.com').toEqual(expect.stringMatching(/\w+@\w+\.\w+/));
    });

    test('objectContaining', () => {
      const user = { id: 1, name: 'John', email: 'john@example.com' };
      expect(user).toEqual(expect.objectContaining({ name: 'John' }));
    });

    test('arrayContaining', () => {
      expect([1, 2, 3, 4]).toEqual(expect.arrayContaining([2, 4]));
    });

    test('not asymmetric matcher', () => {
      expect('hello').toEqual(expect.not.stringContaining('world'));
      expect([1, 2, 3]).toEqual(expect.not.arrayContaining([4, 5]));
    });
  });
});

// TypeScript custom matcher type declaration
declare global {
  namespace jest {
    interface Matchers<R> {
      toBeWithinRange(floor: number, ceiling: number): R;
    }
  }
}
