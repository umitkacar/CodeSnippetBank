// Class Testing Patterns
// Comprehensive examples for testing classes and OOP

describe('Class Testing Patterns', () => {
  // Basic class testing
  describe('Basic Class Tests', () => {
    class Calculator {
      add(a: number, b: number): number {
        return a + b;
      }

      subtract(a: number, b: number): number {
        return a - b;
      }
    }

    test('creates instance', () => {
      const calc = new Calculator();
      expect(calc).toBeInstanceOf(Calculator);
    });

    test('methods work correctly', () => {
      const calc = new Calculator();
      expect(calc.add(2, 3)).toBe(5);
      expect(calc.subtract(5, 2)).toBe(3);
    });
  });

  // Testing class with state
  describe('Stateful Class', () => {
    class Counter {
      private count = 0;

      increment(): void {
        this.count++;
      }

      decrement(): void {
        this.count--;
      }

      getCount(): number {
        return this.count;
      }

      reset(): void {
        this.count = 0;
      }
    }

    let counter: Counter;

    beforeEach(() => {
      counter = new Counter();
    });

    test('starts at zero', () => {
      expect(counter.getCount()).toBe(0);
    });

    test('increments count', () => {
      counter.increment();
      expect(counter.getCount()).toBe(1);
    });

    test('decrements count', () => {
      counter.decrement();
      expect(counter.getCount()).toBe(-1);
    });

    test('resets count', () => {
      counter.increment();
      counter.increment();
      counter.reset();
      expect(counter.getCount()).toBe(0);
    });
  });

  // Testing class with dependencies
  describe('Class with Dependencies', () => {
    interface Logger {
      log(message: string): void;
    }

    class UserService {
      constructor(private logger: Logger) {}

      createUser(name: string): { id: number; name: string } {
        this.logger.log(`Creating user: ${name}`);
        return { id: 1, name };
      }
    }

    test('uses injected dependency', () => {
      const mockLogger = { log: jest.fn() };
      const service = new UserService(mockLogger);

      service.createUser('John');

      expect(mockLogger.log).toHaveBeenCalledWith('Creating user: John');
    });
  });

  // Testing inheritance
  describe('Inheritance', () => {
    class Animal {
      constructor(protected name: string) {}

      makeSound(): string {
        return 'Some sound';
      }

      getName(): string {
        return this.name;
      }
    }

    class Dog extends Animal {
      makeSound(): string {
        return 'Woof!';
      }

      fetch(): string {
        return `${this.name} is fetching`;
      }
    }

    test('inherits from parent', () => {
      const dog = new Dog('Buddy');
      expect(dog).toBeInstanceOf(Dog);
      expect(dog).toBeInstanceOf(Animal);
    });

    test('overrides parent method', () => {
      const dog = new Dog('Buddy');
      expect(dog.makeSound()).toBe('Woof!');
    });

    test('has parent methods', () => {
      const dog = new Dog('Buddy');
      expect(dog.getName()).toBe('Buddy');
    });

    test('has own methods', () => {
      const dog = new Dog('Buddy');
      expect(dog.fetch()).toBe('Buddy is fetching');
    });
  });

  // Testing abstract classes
  describe('Abstract Classes', () => {
    abstract class Shape {
      constructor(protected color: string) {}

      abstract area(): number;

      getColor(): string {
        return this.color;
      }
    }

    class Rectangle extends Shape {
      constructor(
        color: string,
        private width: number,
        private height: number
      ) {
        super(color);
      }

      area(): number {
        return this.width * this.height;
      }
    }

    class Circle extends Shape {
      constructor(color: string, private radius: number) {
        super(color);
      }

      area(): number {
        return Math.PI * this.radius ** 2;
      }
    }

    test('rectangle calculates area', () => {
      const rect = new Rectangle('red', 5, 10);
      expect(rect.area()).toBe(50);
    });

    test('circle calculates area', () => {
      const circle = new Circle('blue', 5);
      expect(circle.area()).toBeCloseTo(78.54, 2);
    });

    test('shapes have color', () => {
      const rect = new Rectangle('red', 5, 10);
      const circle = new Circle('blue', 5);

      expect(rect.getColor()).toBe('red');
      expect(circle.getColor()).toBe('blue');
    });
  });

  // Testing static methods
  describe('Static Methods', () => {
    class MathUtils {
      static add(a: number, b: number): number {
        return a + b;
      }

      static multiply(a: number, b: number): number {
        return a * b;
      }

      static factorial(n: number): number {
        if (n <= 1) return 1;
        return n * this.factorial(n - 1);
      }
    }

    test('static methods work without instance', () => {
      expect(MathUtils.add(2, 3)).toBe(5);
      expect(MathUtils.multiply(4, 5)).toBe(20);
    });

    test('static recursive method', () => {
      expect(MathUtils.factorial(5)).toBe(120);
      expect(MathUtils.factorial(0)).toBe(1);
    });

    test('can spy on static methods', () => {
      const spy = jest.spyOn(MathUtils, 'add');
      MathUtils.add(1, 2);
      expect(spy).toHaveBeenCalledWith(1, 2);
    });
  });

  // Testing getters and setters
  describe('Getters and Setters', () => {
    class User {
      private _email: string = '';

      get email(): string {
        return this._email;
      }

      set email(value: string) {
        if (!value.includes('@')) {
          throw new Error('Invalid email');
        }
        this._email = value;
      }
    }

    test('getter returns value', () => {
      const user = new User();
      user['_email'] = 'test@example.com';
      expect(user.email).toBe('test@example.com');
    });

    test('setter validates value', () => {
      const user = new User();
      expect(() => {
        user.email = 'invalid';
      }).toThrow('Invalid email');
    });

    test('setter accepts valid value', () => {
      const user = new User();
      user.email = 'valid@example.com';
      expect(user.email).toBe('valid@example.com');
    });
  });

  // Testing private methods (indirectly)
  describe('Private Methods', () => {
    class PasswordValidator {
      validate(password: string): boolean {
        return (
          this.hasMinLength(password) &&
          this.hasUpperCase(password) &&
          this.hasLowerCase(password) &&
          this.hasNumber(password)
        );
      }

      private hasMinLength(password: string): boolean {
        return password.length >= 8;
      }

      private hasUpperCase(password: string): boolean {
        return /[A-Z]/.test(password);
      }

      private hasLowerCase(password: string): boolean {
        return /[a-z]/.test(password);
      }

      private hasNumber(password: string): boolean {
        return /[0-9]/.test(password);
      }
    }

    test('validates password through public method', () => {
      const validator = new PasswordValidator();
      expect(validator.validate('Password123')).toBe(true);
      expect(validator.validate('short')).toBe(false);
      expect(validator.validate('nouppercase123')).toBe(false);
    });
  });

  // Testing class composition
  describe('Class Composition', () => {
    class Engine {
      start(): string {
        return 'Engine started';
      }

      stop(): string {
        return 'Engine stopped';
      }
    }

    class Car {
      private engine: Engine;

      constructor() {
        this.engine = new Engine();
      }

      start(): string {
        return this.engine.start();
      }

      stop(): string {
        return this.engine.stop();
      }
    }

    test('car uses engine', () => {
      const car = new Car();
      expect(car.start()).toBe('Engine started');
      expect(car.stop()).toBe('Engine stopped');
    });

    test('can mock composed object', () => {
      const car = new Car();
      const mockEngine = {
        start: jest.fn().mockReturnValue('Mocked start'),
        stop: jest.fn().mockReturnValue('Mocked stop'),
      };

      car['engine'] = mockEngine as any;

      expect(car.start()).toBe('Mocked start');
      expect(mockEngine.start).toHaveBeenCalled();
    });
  });

  // Testing singleton pattern
  describe('Singleton Pattern', () => {
    class Database {
      private static instance: Database;
      private connected = false;

      private constructor() {}

      static getInstance(): Database {
        if (!Database.instance) {
          Database.instance = new Database();
        }
        return Database.instance;
      }

      connect(): void {
        this.connected = true;
      }

      isConnected(): boolean {
        return this.connected;
      }
    }

    test('returns same instance', () => {
      const db1 = Database.getInstance();
      const db2 = Database.getInstance();
      expect(db1).toBe(db2);
    });

    test('maintains state across instances', () => {
      const db1 = Database.getInstance();
      db1.connect();

      const db2 = Database.getInstance();
      expect(db2.isConnected()).toBe(true);
    });
  });

  // Testing factory pattern
  describe('Factory Pattern', () => {
    interface Product {
      getName(): string;
    }

    class ConcreteProductA implements Product {
      getName(): string {
        return 'Product A';
      }
    }

    class ConcreteProductB implements Product {
      getName(): string {
        return 'Product B';
      }
    }

    class ProductFactory {
      create(type: string): Product {
        switch (type) {
          case 'A':
            return new ConcreteProductA();
          case 'B':
            return new ConcreteProductB();
          default:
            throw new Error('Unknown product type');
        }
      }
    }

    test('creates product A', () => {
      const factory = new ProductFactory();
      const product = factory.create('A');
      expect(product.getName()).toBe('Product A');
    });

    test('creates product B', () => {
      const factory = new ProductFactory();
      const product = factory.create('B');
      expect(product.getName()).toBe('Product B');
    });

    test('throws for unknown type', () => {
      const factory = new ProductFactory();
      expect(() => factory.create('C')).toThrow('Unknown product type');
    });
  });
});
