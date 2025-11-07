// Property-Based Testing with fast-check
// Comprehensive property-based testing examples

import fc from 'fast-check';

// Property-based testing discovers edge cases automatically
describe('Property-Based Testing', () => {
  // Example 1: String operations
  describe('String Reversal Properties', () => {
    function reverse(str: string): string {
      return str.split('').reverse().join('');
    }

    test('reversing twice returns original', () => {
      fc.assert(
        fc.property(fc.string(), (str) => {
          const reversed = reverse(reverse(str));
          expect(reversed).toBe(str);
        })
      );
    });

    test('reversed string has same length', () => {
      fc.assert(
        fc.property(fc.string(), (str) => {
          const reversed = reverse(str);
          expect(reversed.length).toBe(str.length);
        })
      );
    });

    test('concatenation reversal property', () => {
      fc.assert(
        fc.property(fc.string(), fc.string(), (str1, str2) => {
          const reversed = reverse(str1 + str2);
          const expected = reverse(str2) + reverse(str1);
          expect(reversed).toBe(expected);
        })
      );
    });
  });

  // Example 2: Arithmetic properties
  describe('Addition Properties', () => {
    test('addition is commutative', () => {
      fc.assert(
        fc.property(fc.integer(), fc.integer(), (a, b) => {
          expect(a + b).toBe(b + a);
        })
      );
    });

    test('addition is associative', () => {
      fc.assert(
        fc.property(fc.integer(), fc.integer(), fc.integer(), (a, b, c) => {
          expect((a + b) + c).toBe(a + (b + c));
        })
      );
    });

    test('zero is identity element', () => {
      fc.assert(
        fc.property(fc.integer(), (n) => {
          expect(n + 0).toBe(n);
          expect(0 + n).toBe(n);
        })
      );
    });
  });

  // Example 3: Array operations
  describe('Array Properties', () => {
    test('map preserves length', () => {
      fc.assert(
        fc.property(fc.array(fc.integer()), (arr) => {
          const mapped = arr.map((x) => x * 2);
          expect(mapped.length).toBe(arr.length);
        })
      );
    });

    test('filter reduces or maintains length', () => {
      fc.assert(
        fc.property(fc.array(fc.integer()), (arr) => {
          const filtered = arr.filter((x) => x > 0);
          expect(filtered.length).toBeLessThanOrEqual(arr.length);
        })
      );
    });

    test('concat combines lengths', () => {
      fc.assert(
        fc.property(fc.array(fc.integer()), fc.array(fc.integer()), (arr1, arr2) => {
          const combined = arr1.concat(arr2);
          expect(combined.length).toBe(arr1.length + arr2.length);
        })
      );
    });

    test('sort does not change length', () => {
      fc.assert(
        fc.property(fc.array(fc.integer()), (arr) => {
          const sorted = [...arr].sort((a, b) => a - b);
          expect(sorted.length).toBe(arr.length);
        })
      );
    });
  });

  // Example 4: Custom data structures
  describe('Stack Properties', () => {
    class Stack<T> {
      private items: T[] = [];

      push(item: T): void {
        this.items.push(item);
      }

      pop(): T | undefined {
        return this.items.pop();
      }

      peek(): T | undefined {
        return this.items[this.items.length - 1];
      }

      size(): number {
        return this.items.length;
      }

      isEmpty(): boolean {
        return this.items.length === 0;
      }
    }

    test('push increases size by 1', () => {
      fc.assert(
        fc.property(fc.integer(), (value) => {
          const stack = new Stack<number>();
          const initialSize = stack.size();
          stack.push(value);
          expect(stack.size()).toBe(initialSize + 1);
        })
      );
    });

    test('push then pop returns same value', () => {
      fc.assert(
        fc.property(fc.integer(), (value) => {
          const stack = new Stack<number>();
          stack.push(value);
          expect(stack.pop()).toBe(value);
        })
      );
    });

    test('multiple push then pop maintains LIFO', () => {
      fc.assert(
        fc.property(fc.array(fc.integer(), { minLength: 1 }), (values) => {
          const stack = new Stack<number>();
          values.forEach((v) => stack.push(v));

          const popped: number[] = [];
          while (!stack.isEmpty()) {
            popped.push(stack.pop()!);
          }

          expect(popped).toEqual([...values].reverse());
        })
      );
    });
  });

  // Example 5: Validation properties
  describe('Email Validation Properties', () => {
    function isValidEmail(email: string): boolean {
      const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return regex.test(email);
    }

    test('email must contain @', () => {
      fc.assert(
        fc.property(fc.emailAddress(), (email) => {
          if (isValidEmail(email)) {
            expect(email).toContain('@');
          }
        })
      );
    });

    test('email must contain domain', () => {
      fc.assert(
        fc.property(fc.emailAddress(), (email) => {
          if (isValidEmail(email)) {
            const parts = email.split('@');
            expect(parts.length).toBe(2);
            expect(parts[1]).toContain('.');
          }
        })
      );
    });
  });

  // Example 6: Number range properties
  describe('Number Range Properties', () => {
    function clamp(value: number, min: number, max: number): number {
      return Math.max(min, Math.min(max, value));
    }

    test('clamped value is within range', () => {
      fc.assert(
        fc.property(
          fc.integer(),
          fc.integer(),
          fc.integer(),
          (value, min, max) => {
            fc.pre(min <= max); // Precondition
            const clamped = clamp(value, min, max);
            expect(clamped).toBeGreaterThanOrEqual(min);
            expect(clamped).toBeLessThanOrEqual(max);
          }
        )
      );
    });

    test('clamping value in range returns same value', () => {
      fc.assert(
        fc.property(fc.integer(), fc.integer(), (min, max) => {
          fc.pre(min <= max);
          const value = min + Math.floor((max - min) / 2);
          expect(clamp(value, min, max)).toBe(value);
        })
      );
    });
  });

  // Example 7: Serialization properties
  describe('JSON Serialization Properties', () => {
    test('parse after stringify is identity', () => {
      fc.assert(
        fc.property(fc.json(), (obj) => {
          const serialized = JSON.stringify(obj);
          const deserialized = JSON.parse(serialized);
          expect(deserialized).toEqual(obj);
        })
      );
    });

    test('stringify produces valid JSON string', () => {
      fc.assert(
        fc.property(fc.json(), (obj) => {
          const serialized = JSON.stringify(obj);
          expect(typeof serialized).toBe('string');
          expect(() => JSON.parse(serialized)).not.toThrow();
        })
      );
    });
  });

  // Example 8: Date properties
  describe('Date Properties', () => {
    test('date comparison is transitive', () => {
      fc.assert(
        fc.property(fc.date(), fc.date(), fc.date(), (d1, d2, d3) => {
          const t1 = d1.getTime();
          const t2 = d2.getTime();
          const t3 = d3.getTime();

          if (t1 <= t2 && t2 <= t3) {
            expect(t1).toBeLessThanOrEqual(t3);
          }
        })
      );
    });

    test('adding days moves forward', () => {
      fc.assert(
        fc.property(fc.date(), fc.nat(365), (date, days) => {
          const future = new Date(date);
          future.setDate(future.getDate() + days);
          expect(future.getTime()).toBeGreaterThanOrEqual(date.getTime());
        })
      );
    });
  });

  // Example 9: Custom arbitraries
  describe('Custom Arbitraries', () => {
    const userArbitrary = fc.record({
      id: fc.nat(),
      name: fc.string({ minLength: 1, maxLength: 50 }),
      email: fc.emailAddress(),
      age: fc.integer({ min: 0, max: 120 }),
      active: fc.boolean(),
    });

    test('user properties are within constraints', () => {
      fc.assert(
        fc.property(userArbitrary, (user) => {
          expect(user.id).toBeGreaterThanOrEqual(0);
          expect(user.name.length).toBeGreaterThan(0);
          expect(user.name.length).toBeLessThanOrEqual(50);
          expect(user.email).toContain('@');
          expect(user.age).toBeGreaterThanOrEqual(0);
          expect(user.age).toBeLessThanOrEqual(120);
          expect(typeof user.active).toBe('boolean');
        })
      );
    });
  });

  // Example 10: Shrinking behavior
  describe('Shrinking Examples', () => {
    test('demonstrates shrinking to minimal failing case', () => {
      try {
        fc.assert(
          fc.property(fc.array(fc.integer()), (arr) => {
            // This will fail and shrink to minimal case
            expect(arr.length).toBeLessThan(5);
          }),
          { numRuns: 100 }
        );
      } catch (error) {
        // Property will find minimal array that violates property
        expect(error).toBeDefined();
      }
    });
  });
});
