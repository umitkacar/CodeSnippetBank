/**
 * Async/Await Patterns in Node.js
 */

// Basic async function
export async function fetchData(url: string): Promise<any> {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching data:', error);
    throw error;
  }
}

// Sequential async operations
export async function sequentialOperations(): Promise<void> {
  try {
    const result1 = await operation1();
    const result2 = await operation2(result1);
    const result3 = await operation3(result2);
    console.log('All operations completed', result3);
  } catch (error) {
    console.error('Operation failed:', error);
    throw error;
  }
}

// Parallel async operations
export async function parallelOperations(): Promise<any[]> {
  try {
    const [result1, result2, result3] = await Promise.all([
      operation1(),
      operation2(),
      operation3(),
    ]);
    return [result1, result2, result3];
  } catch (error) {
    console.error('Parallel operations failed:', error);
    throw error;
  }
}

// Async with timeout
export async function withTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number
): Promise<T> {
  const timeout = new Promise<never>((_, reject) => {
    setTimeout(() => reject(new Error('Operation timed out')), timeoutMs);
  });
  return Promise.race([promise, timeout]);
}

// Helper functions
async function operation1(): Promise<string> {
  return new Promise((resolve) => {
    setTimeout(() => resolve('Result 1'), 100);
  });
}

async function operation2(input?: any): Promise<string> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(`Result 2 (${input})`), 100);
  });
}

async function operation3(input?: any): Promise<string> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(`Result 3 (${input})`), 100);
  });
}
