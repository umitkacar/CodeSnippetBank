// Jest Basic Test Setup
// Production-ready Jest configuration and basic test examples

describe('Calculator', () => {
  test('adds two numbers correctly', () => {
    expect(2 + 2).toBe(4);
  });

  test('subtracts two numbers correctly', () => {
    expect(5 - 3).toBe(2);
  });

  test('multiplies two numbers correctly', () => {
    expect(3 * 4).toBe(12);
  });

  test('divides two numbers correctly', () => {
    expect(10 / 2).toBe(5);
  });

  test('handles division by zero', () => {
    expect(() => {
      if (2 / 0 === Infinity) throw new Error('Division by zero');
    }).toThrow('Division by zero');
  });
});

// Async testing
describe('Async Operations', () => {
  test('resolves promise', async () => {
    const data = await Promise.resolve('success');
    expect(data).toBe('success');
  });

  test('rejects promise', async () => {
    await expect(Promise.reject('error')).rejects.toBe('error');
  });
});

// Using beforeEach and afterEach
describe('Lifecycle Hooks', () => {
  let counter: number;

  beforeEach(() => {
    counter = 0;
  });

  afterEach(() => {
    counter = 0;
  });

  test('increments counter', () => {
    counter++;
    expect(counter).toBe(1);
  });

  test('counter starts at 0', () => {
    expect(counter).toBe(0);
  });
});
