/**
 * Promise Patterns in Node.js
 */

// Create a promise
export function createPromise<T>(value: T, delay: number = 1000): Promise<T> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (value) {
        resolve(value);
      } else {
        reject(new Error('Value is falsy'));
      }
    }, delay);
  });
}

// Promise chaining
export function promiseChaining(): Promise<string> {
  return createPromise('Initial')
    .then((result) => {
      console.log(result);
      return createPromise('Second', 500);
    })
    .then((result) => {
      console.log(result);
      return createPromise('Final', 500);
    })
    .catch((error) => {
      console.error('Error in chain:', error);
      throw error;
    });
}

// Promise.all
export function promiseAll(): Promise<any[]> {
  const promises = [
    createPromise('One', 1000),
    createPromise('Two', 500),
    createPromise('Three', 750),
  ];
  return Promise.all(promises);
}

// Promise.race
export function promiseRace(): Promise<any> {
  const promises = [
    createPromise('Slow', 2000),
    createPromise('Fast', 500),
    createPromise('Medium', 1000),
  ];
  return Promise.race(promises);
}

// Promise.allSettled
export function promiseAllSettled(): Promise<PromiseSettledResult<any>[]> {
  const promises = [
    createPromise('Success', 1000),
    Promise.reject(new Error('Failed')),
    createPromise('Another Success', 500),
  ];
  return Promise.allSettled(promises);
}

// Promise.any
export function promiseAny(): Promise<any> {
  const promises = [
    Promise.reject(new Error('Error 1')),
    createPromise('First Success', 1000),
    createPromise('Second Success', 500),
  ];
  return Promise.any(promises);
}

// Retry with exponential backoff
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      const delay = baseDelay * Math.pow(2, i);
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }
  throw new Error('Max retries exceeded');
}
