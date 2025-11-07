// Performance Testing Helpers
// Utilities for measuring performance

export class PerformanceHelpers {
  static measure(fn: () => void): number {
    const start = performance.now();
    fn();
    return performance.now() - start;
  }

  static async measureAsync(fn: () => Promise<void>): Promise<number> {
    const start = performance.now();
    await fn();
    return performance.now() - start;
  }

  static benchmark(fn: () => void, iterations = 1000): {
    avg: number;
    min: number;
    max: number;
  } {
    const times: number[] = [];

    for (let i = 0; i < iterations; i++) {
      const start = performance.now();
      fn();
      times.push(performance.now() - start);
    }

    return {
      avg: times.reduce((a, b) => a + b) / times.length,
      min: Math.min(...times),
      max: Math.max(...times),
    };
  }
}

describe('Performance Helpers', () => {
  test('measures execution time', () => {
    const time = PerformanceHelpers.measure(() => {
      for (let i = 0; i < 1000; i++) {}
    });
    expect(time).toBeGreaterThanOrEqual(0);
  });

  test('benchmarks function', () => {
    const stats = PerformanceHelpers.benchmark(() => {
      Math.random();
    }, 100);

    expect(stats.avg).toBeGreaterThan(0);
    expect(stats.min).toBeLessThanOrEqual(stats.avg);
    expect(stats.max).toBeGreaterThanOrEqual(stats.avg);
  });
});
