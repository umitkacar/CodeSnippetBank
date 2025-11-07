// Spy Patterns and Techniques
// Comprehensive spy examples for testing

import { jest } from '@jest/globals';

// Class to spy on
class Logger {
  log(message: string): void {
    console.log(message);
  }

  error(message: string): void {
    console.error(message);
  }

  warn(message: string): void {
    console.warn(message);
  }

  info(message: string): void {
    console.info(message);
  }
}

class UserService {
  constructor(private logger: Logger) {}

  createUser(name: string, email: string): { id: number; name: string; email: string } {
    this.logger.log(`Creating user: ${name}`);
    const user = { id: Math.random(), name, email };
    this.logger.log(`User created with ID: ${user.id}`);
    return user;
  }

  deleteUser(id: number): void {
    this.logger.warn(`Deleting user: ${id}`);
    // Deletion logic here
    this.logger.log(`User ${id} deleted`);
  }

  handleError(error: Error): void {
    this.logger.error(`Error occurred: ${error.message}`);
  }
}

// Spy patterns
describe('Spy Patterns', () => {
  let logger: Logger;
  let service: UserService;

  beforeEach(() => {
    logger = new Logger();
    service = new UserService(logger);
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Basic Spying', () => {
    test('spies on method calls', () => {
      const spy = jest.spyOn(logger, 'log');

      service.createUser('John', 'john@example.com');

      expect(spy).toHaveBeenCalled();
      expect(spy).toHaveBeenCalledTimes(2);
    });

    test('spies on method with specific arguments', () => {
      const spy = jest.spyOn(logger, 'log');

      service.createUser('Jane', 'jane@example.com');

      expect(spy).toHaveBeenCalledWith(expect.stringContaining('Creating user'));
      expect(spy).toHaveBeenCalledWith(expect.stringContaining('User created'));
    });

    test('spies without affecting implementation', () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();

      logger.log('test message');

      expect(consoleLogSpy).toHaveBeenCalledWith('test message');
    });
  });

  describe('Spy Mock Implementation', () => {
    test('spies and overrides implementation', () => {
      const spy = jest.spyOn(logger, 'log').mockImplementation((message) => {
        // Custom implementation
      });

      logger.log('test');

      expect(spy).toHaveBeenCalledWith('test');
      spy.mockRestore();
    });

    test('spies with return value', () => {
      class Calculator {
        add(a: number, b: number): number {
          return a + b;
        }
      }

      const calc = new Calculator();
      const spy = jest.spyOn(calc, 'add').mockReturnValue(100);

      expect(calc.add(2, 3)).toBe(100);
      expect(spy).toHaveBeenCalledWith(2, 3);
    });
  });

  describe('Multiple Spies', () => {
    test('spies on multiple methods', () => {
      const logSpy = jest.spyOn(logger, 'log');
      const warnSpy = jest.spyOn(logger, 'warn');

      service.deleteUser(123);

      expect(logSpy).toHaveBeenCalled();
      expect(warnSpy).toHaveBeenCalled();
    });

    test('tracks call order', () => {
      const logSpy = jest.spyOn(logger, 'log');
      const errorSpy = jest.spyOn(logger, 'error');

      service.createUser('John', 'john@example.com');
      service.handleError(new Error('Test error'));

      expect(logSpy).toHaveBeenCalled();
      expect(errorSpy).toHaveBeenCalledAfter(logSpy);
    });
  });

  describe('Spy Assertions', () => {
    test('asserts call count', () => {
      const spy = jest.spyOn(logger, 'log');

      logger.log('message 1');
      logger.log('message 2');
      logger.log('message 3');

      expect(spy).toHaveBeenCalledTimes(3);
    });

    test('asserts first call', () => {
      const spy = jest.spyOn(logger, 'log');

      logger.log('first');
      logger.log('second');

      expect(spy).toHaveBeenNthCalledWith(1, 'first');
      expect(spy).toHaveBeenNthCalledWith(2, 'second');
    });

    test('asserts last call', () => {
      const spy = jest.spyOn(logger, 'log');

      logger.log('first');
      logger.log('last');

      expect(spy).toHaveBeenLastCalledWith('last');
    });
  });

  describe('Spy Return Values', () => {
    test('tracks return values', () => {
      class DataService {
        getData(): string {
          return 'real data';
        }
      }

      const service = new DataService();
      const spy = jest.spyOn(service, 'getData');

      const result = service.getData();

      expect(spy).toHaveReturnedWith('real data');
      expect(result).toBe('real data');
    });

    test('mocks return values', () => {
      class ApiClient {
        async fetchData(): Promise<any> {
          return { data: 'real' };
        }
      }

      const client = new ApiClient();
      const spy = jest.spyOn(client, 'fetchData').mockResolvedValue({ data: 'mocked' });

      return client.fetchData().then((data) => {
        expect(data).toEqual({ data: 'mocked' });
        expect(spy).toHaveBeenCalled();
      });
    });
  });

  describe('Spy Cleanup', () => {
    test('restores original implementation', () => {
      const original = logger.log;
      const spy = jest.spyOn(logger, 'log').mockImplementation();

      logger.log('mocked');
      expect(spy).toHaveBeenCalled();

      spy.mockRestore();
      // Now uses original implementation
    });

    test('clears spy history', () => {
      const spy = jest.spyOn(logger, 'log');

      logger.log('first');
      expect(spy).toHaveBeenCalledTimes(1);

      spy.mockClear();
      expect(spy).toHaveBeenCalledTimes(0);

      logger.log('second');
      expect(spy).toHaveBeenCalledTimes(1);
    });

    test('resets spy', () => {
      const spy = jest.spyOn(logger, 'log').mockReturnValue(undefined);

      logger.log('test');
      expect(spy).toHaveBeenCalled();

      spy.mockReset();
      expect(spy).toHaveBeenCalledTimes(0);
    });
  });

  describe('Spy on Getters/Setters', () => {
    class Config {
      private _value: string = 'default';

      get value(): string {
        return this._value;
      }

      set value(val: string) {
        this._value = val;
      }
    }

    test('spies on getter', () => {
      const config = new Config();
      const spy = jest.spyOn(config, 'value', 'get').mockReturnValue('mocked');

      expect(config.value).toBe('mocked');
      expect(spy).toHaveBeenCalled();
    });

    test('spies on setter', () => {
      const config = new Config();
      const spy = jest.spyOn(config, 'value', 'set');

      config.value = 'new value';

      expect(spy).toHaveBeenCalledWith('new value');
    });
  });

  describe('Spy on Static Methods', () => {
    class MathUtils {
      static add(a: number, b: number): number {
        return a + b;
      }

      static multiply(a: number, b: number): number {
        return a * b;
      }
    }

    test('spies on static method', () => {
      const spy = jest.spyOn(MathUtils, 'add');

      MathUtils.add(2, 3);

      expect(spy).toHaveBeenCalledWith(2, 3);
      expect(spy).toHaveReturnedWith(5);
    });

    test('mocks static method', () => {
      const spy = jest.spyOn(MathUtils, 'multiply').mockReturnValue(100);

      expect(MathUtils.multiply(2, 3)).toBe(100);
      expect(spy).toHaveBeenCalled();
    });
  });
});

// Advanced spy patterns
describe('Advanced Spy Patterns', () => {
  describe('Conditional Spying', () => {
    class PaymentService {
      processPayment(amount: number): boolean {
        if (amount > 0) {
          return true;
        }
        return false;
      }
    }

    test('spies based on condition', () => {
      const service = new PaymentService();
      const spy = jest.spyOn(service, 'processPayment');

      service.processPayment(100);
      service.processPayment(-50);

      expect(spy).toHaveBeenCalledTimes(2);
      expect(spy).toHaveNthReturnedWith(1, true);
      expect(spy).toHaveNthReturnedWith(2, false);
    });
  });

  describe('Spy Chains', () => {
    class Database {
      connect(): this {
        return this;
      }

      query(): this {
        return this;
      }

      disconnect(): void {}
    }

    test('spies on method chains', () => {
      const db = new Database();
      const connectSpy = jest.spyOn(db, 'connect');
      const querySpy = jest.spyOn(db, 'query');
      const disconnectSpy = jest.spyOn(db, 'disconnect');

      db.connect().query().disconnect();

      expect(connectSpy).toHaveBeenCalled();
      expect(querySpy).toHaveBeenCalled();
      expect(disconnectSpy).toHaveBeenCalled();
    });
  });
});
