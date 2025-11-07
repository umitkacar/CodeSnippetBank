// Functional Programming Testing
// Testing pure functions, composition, and functional patterns

describe('Functional Programming Testing', () => {
  // Pure functions
  describe('Pure Functions', () => {
    const add = (a: number, b: number): number => a + b;
    const multiply = (a: number, b: number): number => a * b;
    const square = (n: number): number => n * n;

    test('pure functions return same output for same input', () => {
      expect(add(2, 3)).toBe(5);
      expect(add(2, 3)).toBe(5);
      expect(add(2, 3)).toBe(5);
    });

    test('pure functions have no side effects', () => {
      const arr = [1, 2, 3];
      const doubled = arr.map(x => x * 2);

      expect(arr).toEqual([1, 2, 3]); // Original unchanged
      expect(doubled).toEqual([2, 4, 6]);
    });

    test('pure functions are composable', () => {
      const addThenSquare = (a: number, b: number) => square(add(a, b));
      expect(addThenSquare(2, 3)).toBe(25); // (2+3)^2
    });
  });

  // Function composition
  describe('Function Composition', () => {
    const compose = <T>(...fns: Array<(arg: T) => T>) =>
      (x: T) => fns.reduceRight((acc, fn) => fn(acc), x);

    const pipe = <T>(...fns: Array<(arg: T) => T>) =>
      (x: T) => fns.reduce((acc, fn) => fn(acc), x);

    const double = (x: number) => x * 2;
    const increment = (x: number) => x + 1;
    const square = (x: number) => x * x;

    test('compose executes right to left', () => {
      const doubleThenIncrement = compose(increment, double);
      expect(doubleThenIncrement(5)).toBe(11); // (5*2)+1
    });

    test('pipe executes left to right', () => {
      const doubleThenIncrement = pipe(double, increment);
      expect(doubleThenIncrement(5)).toBe(11); // (5*2)+1
    });

    test('complex composition', () => {
      const fn = compose(square, increment, double);
      expect(fn(2)).toBe(25); // ((2*2)+1)^2 = 5^2 = 25
    });
  });

  // Higher-order functions
  describe('Higher-Order Functions', () => {
    const map = <T, U>(fn: (item: T) => U) => (arr: T[]): U[] =>
      arr.map(fn);

    const filter = <T>(predicate: (item: T) => boolean) => (arr: T[]): T[] =>
      arr.filter(predicate);

    const reduce = <T, U>(fn: (acc: U, item: T) => U, initial: U) => (arr: T[]): U =>
      arr.reduce(fn, initial);

    test('map higher-order function', () => {
      const double = map((x: number) => x * 2);
      expect(double([1, 2, 3])).toEqual([2, 4, 6]);
    });

    test('filter higher-order function', () => {
      const evens = filter((x: number) => x % 2 === 0);
      expect(evens([1, 2, 3, 4, 5])).toEqual([2, 4]);
    });

    test('reduce higher-order function', () => {
      const sum = reduce((acc: number, x: number) => acc + x, 0);
      expect(sum([1, 2, 3, 4])).toBe(10);
    });

    test('chaining higher-order functions', () => {
      const double = map((x: number) => x * 2);
      const evens = filter((x: number) => x % 2 === 0);
      const sum = reduce((acc: number, x: number) => acc + x, 0);

      const result = sum(double(evens([1, 2, 3, 4, 5])));
      expect(result).toBe(12); // evens: [2,4], doubled: [4,8], sum: 12
    });
  });

  // Currying
  describe('Currying', () => {
    const curry = <A, B, C>(fn: (a: A, b: B) => C) =>
      (a: A) => (b: B) => fn(a, b);

    const add = (a: number, b: number) => a + b;
    const multiply = (a: number, b: number) => a * b;

    test('curries binary function', () => {
      const curriedAdd = curry(add);
      const add5 = curriedAdd(5);

      expect(add5(3)).toBe(8);
      expect(add5(10)).toBe(15);
    });

    test('partial application', () => {
      const curriedMultiply = curry(multiply);
      const double = curriedMultiply(2);
      const triple = curriedMultiply(3);

      expect(double(4)).toBe(8);
      expect(triple(4)).toBe(12);
    });
  });

  // Immutability
  describe('Immutability', () => {
    const updateProp = <T extends object, K extends keyof T>(
      obj: T,
      key: K,
      value: T[K]
    ): T => ({
      ...obj,
      [key]: value,
    });

    const addToArray = <T>(arr: T[], item: T): T[] => [...arr, item];

    const removeFromArray = <T>(arr: T[], index: number): T[] => [
      ...arr.slice(0, index),
      ...arr.slice(index + 1),
    ];

    test('immutable object update', () => {
      const original = { name: 'John', age: 30 };
      const updated = updateProp(original, 'age', 31);

      expect(original.age).toBe(30);
      expect(updated.age).toBe(31);
      expect(original).not.toBe(updated);
    });

    test('immutable array addition', () => {
      const original = [1, 2, 3];
      const updated = addToArray(original, 4);

      expect(original).toEqual([1, 2, 3]);
      expect(updated).toEqual([1, 2, 3, 4]);
      expect(original).not.toBe(updated);
    });

    test('immutable array removal', () => {
      const original = [1, 2, 3, 4];
      const updated = removeFromArray(original, 1);

      expect(original).toEqual([1, 2, 3, 4]);
      expect(updated).toEqual([1, 3, 4]);
    });
  });

  // Monads (Option/Maybe)
  describe('Option Monad', () => {
    class Option<T> {
      private constructor(private value: T | null) {}

      static some<T>(value: T): Option<T> {
        return new Option(value);
      }

      static none<T>(): Option<T> {
        return new Option<T>(null);
      }

      map<U>(fn: (value: T) => U): Option<U> {
        return this.value !== null ? Option.some(fn(this.value)) : Option.none();
      }

      flatMap<U>(fn: (value: T) => Option<U>): Option<U> {
        return this.value !== null ? fn(this.value) : Option.none();
      }

      getOrElse(defaultValue: T): T {
        return this.value !== null ? this.value : defaultValue;
      }

      isSome(): boolean {
        return this.value !== null;
      }

      isNone(): boolean {
        return this.value === null;
      }
    }

    test('Option with value', () => {
      const opt = Option.some(5);
      expect(opt.isSome()).toBe(true);
      expect(opt.isNone()).toBe(false);
      expect(opt.getOrElse(0)).toBe(5);
    });

    test('Option without value', () => {
      const opt = Option.none<number>();
      expect(opt.isNone()).toBe(true);
      expect(opt.isSome()).toBe(false);
      expect(opt.getOrElse(0)).toBe(0);
    });

    test('Option map', () => {
      const opt = Option.some(5);
      const doubled = opt.map(x => x * 2);
      expect(doubled.getOrElse(0)).toBe(10);

      const none = Option.none<number>();
      const mapped = none.map(x => x * 2);
      expect(mapped.getOrElse(0)).toBe(0);
    });

    test('Option flatMap', () => {
      const opt = Option.some(5);
      const result = opt.flatMap(x => x > 0 ? Option.some(x * 2) : Option.none());
      expect(result.getOrElse(0)).toBe(10);
    });
  });

  // Recursive functions
  describe('Recursive Functions', () => {
    const factorial = (n: number): number =>
      n <= 1 ? 1 : n * factorial(n - 1);

    const fibonacci = (n: number): number =>
      n <= 1 ? n : fibonacci(n - 1) + fibonacci(n - 2);

    const sum = (arr: number[]): number =>
      arr.length === 0 ? 0 : arr[0] + sum(arr.slice(1));

    test('factorial', () => {
      expect(factorial(0)).toBe(1);
      expect(factorial(1)).toBe(1);
      expect(factorial(5)).toBe(120);
    });

    test('fibonacci', () => {
      expect(fibonacci(0)).toBe(0);
      expect(fibonacci(1)).toBe(1);
      expect(fibonacci(6)).toBe(8);
    });

    test('recursive sum', () => {
      expect(sum([])).toBe(0);
      expect(sum([1])).toBe(1);
      expect(sum([1, 2, 3, 4])).toBe(10);
    });
  });

  // Lazy evaluation
  describe('Lazy Evaluation', () => {
    function* range(start: number, end: number) {
      for (let i = start; i < end; i++) {
        yield i;
      }
    }

    function* map<T, U>(fn: (item: T) => U, iterable: Iterable<T>) {
      for (const item of iterable) {
        yield fn(item);
      }
    }

    function* filter<T>(predicate: (item: T) => boolean, iterable: Iterable<T>) {
      for (const item of iterable) {
        if (predicate(item)) {
          yield item;
        }
      }
    }

    const take = <T>(n: number, iterable: Iterable<T>): T[] => {
      const result: T[] = [];
      const iterator = iterable[Symbol.iterator]();

      for (let i = 0; i < n; i++) {
        const { value, done } = iterator.next();
        if (done) break;
        result.push(value);
      }

      return result;
    };

    test('lazy range', () => {
      const numbers = range(0, 1000000);
      const first5 = take(5, numbers);
      expect(first5).toEqual([0, 1, 2, 3, 4]);
    });

    test('lazy map and filter', () => {
      const numbers = range(0, 100);
      const evens = filter((x: number) => x % 2 === 0, numbers);
      const doubled = map((x: number) => x * 2, evens);
      const first3 = take(3, doubled);

      expect(first3).toEqual([0, 4, 8]);
    });
  });

  // Memoization
  describe('Memoization', () => {
    const memoize = <T extends (...args: any[]) => any>(fn: T): T => {
      const cache = new Map<string, ReturnType<T>>();

      return ((...args: Parameters<T>) => {
        const key = JSON.stringify(args);
        if (cache.has(key)) {
          return cache.get(key);
        }
        const result = fn(...args);
        cache.set(key, result);
        return result;
      }) as T;
    };

    test('memoizes function results', () => {
      let callCount = 0;
      const expensiveFn = (n: number) => {
        callCount++;
        return n * 2;
      };

      const memoized = memoize(expensiveFn);

      expect(memoized(5)).toBe(10);
      expect(callCount).toBe(1);

      expect(memoized(5)).toBe(10);
      expect(callCount).toBe(1); // Not called again

      expect(memoized(10)).toBe(20);
      expect(callCount).toBe(2);
    });
  });
});
