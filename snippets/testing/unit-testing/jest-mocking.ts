// Jest Mocking Patterns
// Advanced mocking techniques for Jest

// Mock function
const mockCallback = jest.fn((x: number) => 42 + x);

describe('Mock Functions', () => {
  beforeEach(() => {
    mockCallback.mockClear();
  });

  test('mock function is called', () => {
    [0, 1].forEach(mockCallback);
    expect(mockCallback).toHaveBeenCalledTimes(2);
  });

  test('mock function returns value', () => {
    const result = mockCallback(1);
    expect(result).toBe(43);
  });

  test('mock function called with specific arguments', () => {
    mockCallback(5);
    expect(mockCallback).toHaveBeenCalledWith(5);
  });
});

// Mock module
jest.mock('./user-service');
import { UserService } from './user-service';

describe('Mocked Module', () => {
  test('mocks UserService', () => {
    const mockUserService = UserService as jest.MockedClass<typeof UserService>;
    mockUserService.prototype.getUser.mockReturnValue({
      id: 1,
      name: 'John Doe',
      email: 'john@example.com',
    });

    const service = new UserService();
    const user = service.getUser(1);

    expect(user.name).toBe('John Doe');
  });
});

// Mock implementation
const mockFn = jest.fn();

describe('Mock Implementations', () => {
  test('mock implementation once', () => {
    mockFn
      .mockImplementationOnce(() => 'first call')
      .mockImplementationOnce(() => 'second call')
      .mockImplementation(() => 'default');

    expect(mockFn()).toBe('first call');
    expect(mockFn()).toBe('second call');
    expect(mockFn()).toBe('default');
  });
});

// Spy on methods
class Calculator {
  add(a: number, b: number): number {
    return a + b;
  }
}

describe('Spying', () => {
  test('spies on method', () => {
    const calc = new Calculator();
    const spy = jest.spyOn(calc, 'add');

    calc.add(1, 2);
    expect(spy).toHaveBeenCalledWith(1, 2);
    expect(spy).toHaveReturnedWith(3);

    spy.mockRestore();
  });
});

// Mock return values
describe('Mock Return Values', () => {
  test('mock return value once', () => {
    const mockFn = jest.fn();
    mockFn.mockReturnValueOnce(10).mockReturnValueOnce(20).mockReturnValue(30);

    expect(mockFn()).toBe(10);
    expect(mockFn()).toBe(20);
    expect(mockFn()).toBe(30);
  });

  test('mock resolved value', async () => {
    const mockFn = jest.fn();
    mockFn.mockResolvedValue('success');

    await expect(mockFn()).resolves.toBe('success');
  });

  test('mock rejected value', async () => {
    const mockFn = jest.fn();
    mockFn.mockRejectedValue(new Error('failure'));

    await expect(mockFn()).rejects.toThrow('failure');
  });
});
