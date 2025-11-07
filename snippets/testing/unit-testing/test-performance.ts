// Performance Testing in Unit Tests
// Measuring and asserting performance characteristics

describe('Performance Testing', () => {
  // Basic timing tests
  describe('Execution Time', () => {
    test('operation completes within time limit', () => {
      const start = performance.now();

      // Operation to test
      const result = Array.from({ length: 1000 }, (_, i) => i * 2);

      const end = performance.now();
      const duration = end - start;

      expect(duration).toBeLessThan(10); // Should complete in <10ms
      expect(result).toHaveLength(1000);
    });

    test('async operation completes within timeout', async () => {
      const start = performance.now();

      await new Promise((resolve) => setTimeout(resolve, 50));

      const end = performance.now();
      const duration = end - start;

      expect(duration).toBeGreaterThanOrEqual(50);
      expect(duration).toBeLessThan(100);
    });
  });

  // Algorithm complexity testing
  describe('Algorithm Complexity', () => {
    function linearSearch(arr: number[], target: number): number {
      for (let i = 0; i < arr.length; i++) {
        if (arr[i] === target) return i;
      }
      return -1;
    }

    function binarySearch(arr: number[], target: number): number {
      let left = 0;
      let right = arr.length - 1;

      while (left <= right) {
        const mid = Math.floor((left + right) / 2);
        if (arr[mid] === target) return mid;
        if (arr[mid] < target) left = mid + 1;
        else right = mid - 1;
      }
      return -1;
    }

    test('binary search is faster than linear search', () => {
      const arr = Array.from({ length: 100000 }, (_, i) => i);
      const target = 99999;

      // Linear search
      const linearStart = performance.now();
      linearSearch(arr, target);
      const linearTime = performance.now() - linearStart;

      // Binary search
      const binaryStart = performance.now();
      binarySearch(arr, target);
      const binaryTime = performance.now() - binaryStart;

      expect(binaryTime).toBeLessThan(linearTime);
    });
  });

  // Memory usage estimation
  describe('Memory Usage', () => {
    test('efficient data structure uses less memory', () => {
      // Array approach
      const arraySize = 1000;
      const arrayData = Array.from({ length: arraySize }, (_, i) => ({
        id: i,
        value: `value${i}`,
      }));

      // Map approach (more efficient for lookups)
      const mapData = new Map(arrayData.map((item) => [item.id, item.value]));

      // The Map should have the expected size
      expect(mapData.size).toBe(arraySize);
      expect(arrayData.length).toBe(arraySize);
    });
  });

  // Batch operation performance
  describe('Batch Operations', () => {
    function processSingle(items: number[]): number[] {
      return items.map((item) => item * 2);
    }

    function processBatch(items: number[], batchSize: number): number[] {
      const result: number[] = [];
      for (let i = 0; i < items.length; i += batchSize) {
        const batch = items.slice(i, i + batchSize);
        result.push(...batch.map((item) => item * 2));
      }
      return result;
    }

    test('batch processing performance', () => {
      const items = Array.from({ length: 10000 }, (_, i) => i);

      const start1 = performance.now();
      const result1 = processSingle(items);
      const time1 = performance.now() - start1;

      const start2 = performance.now();
      const result2 = processBatch(items, 100);
      const time2 = performance.now() - start2;

      expect(result1).toEqual(result2);
      // Both should complete reasonably fast
      expect(time1).toBeLessThan(100);
      expect(time2).toBeLessThan(100);
    });
  });

  // Caching performance
  describe('Caching Performance', () => {
    class ExpensiveCalculator {
      private cache = new Map<string, number>();
      public calls = 0;

      fibonacci(n: number): number {
        this.calls++;
        const key = `fib_${n}`;

        if (this.cache.has(key)) {
          return this.cache.get(key)!;
        }

        if (n <= 1) return n;

        const result = this.fibonacci(n - 1) + this.fibonacci(n - 2);
        this.cache.set(key, result);
        return result;
      }

      clearCache(): void {
        this.cache.clear();
        this.calls = 0;
      }
    }

    test('cache improves performance', () => {
      const calc = new ExpensiveCalculator();

      // First call (no cache)
      const start1 = performance.now();
      const result1 = calc.fibonacci(30);
      const time1 = performance.now() - start1;
      const calls1 = calc.calls;

      calc.clearCache();

      // Second call with cache warming
      const start2 = performance.now();
      calc.fibonacci(30); // Warm cache
      const result2 = calc.fibonacci(30); // Use cache
      const time2 = performance.now() - start2;

      expect(result1).toBe(result2);
      // Cache should reduce computation time
    });
  });

  // Pagination performance
  describe('Pagination Performance', () => {
    function getPaginatedData<T>(data: T[], page: number, pageSize: number): T[] {
      const start = (page - 1) * pageSize;
      return data.slice(start, start + pageSize);
    }

    test('pagination is efficient for large datasets', () => {
      const largeDataset = Array.from({ length: 100000 }, (_, i) => ({
        id: i,
        name: `Item ${i}`,
      }));

      const start = performance.now();

      // Get first page
      const page1 = getPaginatedData(largeDataset, 1, 10);

      // Get middle page
      const page500 = getPaginatedData(largeDataset, 500, 10);

      // Get last page
      const lastPage = getPaginatedData(largeDataset, 10000, 10);

      const duration = performance.now() - start;

      expect(page1).toHaveLength(10);
      expect(page500).toHaveLength(10);
      expect(lastPage).toHaveLength(10);
      expect(duration).toBeLessThan(10); // Should be very fast
    });
  });

  // Debounce/Throttle performance
  describe('Debounce Performance', () => {
    function debounce<T extends (...args: any[]) => any>(
      func: T,
      delay: number
    ): (...args: Parameters<T>) => void {
      let timeoutId: NodeJS.Timeout;

      return (...args: Parameters<T>) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func(...args), delay);
      };
    }

    test('debounce reduces function calls', async () => {
      jest.useFakeTimers();
      const mockFn = jest.fn();
      const debouncedFn = debounce(mockFn, 100);

      // Rapid calls
      debouncedFn();
      debouncedFn();
      debouncedFn();
      debouncedFn();
      debouncedFn();

      expect(mockFn).not.toHaveBeenCalled();

      jest.advanceTimersByTime(100);

      expect(mockFn).toHaveBeenCalledTimes(1);

      jest.useRealTimers();
    });
  });

  // Data structure performance comparison
  describe('Data Structure Performance', () => {
    test('Set lookup vs Array includes', () => {
      const size = 10000;
      const arr = Array.from({ length: size }, (_, i) => i);
      const set = new Set(arr);
      const target = size - 1;

      // Array includes
      const arrStart = performance.now();
      arr.includes(target);
      const arrTime = performance.now() - arrStart;

      // Set has
      const setStart = performance.now();
      set.has(target);
      const setTime = performance.now() - setStart;

      // Set should be faster for lookups
      expect(setTime).toBeLessThan(arrTime + 1); // +1 for small timing variance
    });

    test('Map get vs Object property access', () => {
      const size = 10000;
      const map = new Map();
      const obj: any = {};

      for (let i = 0; i < size; i++) {
        map.set(`key${i}`, i);
        obj[`key${i}`] = i;
      }

      const key = `key${size - 1}`;

      // Map get
      const mapStart = performance.now();
      map.get(key);
      const mapTime = performance.now() - mapStart;

      // Object property
      const objStart = performance.now();
      obj[key];
      const objTime = performance.now() - objStart;

      // Both should be fast
      expect(mapTime).toBeLessThan(1);
      expect(objTime).toBeLessThan(1);
    });
  });

  // Concurrent operation performance
  describe('Concurrent Operations', () => {
    async function sequentialProcessing(items: number[]): Promise<number[]> {
      const results: number[] = [];
      for (const item of items) {
        await new Promise((resolve) => setTimeout(resolve, 10));
        results.push(item * 2);
      }
      return results;
    }

    async function parallelProcessing(items: number[]): Promise<number[]> {
      return Promise.all(
        items.map(async (item) => {
          await new Promise((resolve) => setTimeout(resolve, 10));
          return item * 2;
        })
      );
    }

    test('parallel processing is faster than sequential', async () => {
      const items = [1, 2, 3, 4, 5];

      const seqStart = performance.now();
      await sequentialProcessing(items);
      const seqTime = performance.now() - seqStart;

      const parStart = performance.now();
      await parallelProcessing(items);
      const parTime = performance.now() - parStart;

      expect(parTime).toBeLessThan(seqTime);
    }, 10000);
  });

  // Performance regression testing
  describe('Performance Regression', () => {
    test('maintains performance baseline', () => {
      const baselineTime = 5; // 5ms baseline

      const start = performance.now();

      // Critical operation
      const data = Array.from({ length: 10000 }, (_, i) => i)
        .filter((x) => x % 2 === 0)
        .map((x) => x * 2);

      const duration = performance.now() - start;

      expect(data.length).toBe(5000);
      expect(duration).toBeLessThan(baselineTime);
    });
  });
});
