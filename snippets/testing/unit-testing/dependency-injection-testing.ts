// Dependency Injection Testing
// Testing patterns for DI containers and injection

describe('Dependency Injection Testing', () => {
  // Constructor injection
  describe('Constructor Injection', () => {
    interface ILogger {
      log(message: string): void;
    }

    interface IDatabase {
      query(sql: string): Promise<any>;
    }

    class UserService {
      constructor(
        private logger: ILogger,
        private database: IDatabase
      ) {}

      async getUser(id: number) {
        this.logger.log(`Getting user ${id}`);
        return this.database.query(`SELECT * FROM users WHERE id = ${id}`);
      }
    }

    test('injects mock dependencies', async () => {
      const mockLogger = { log: jest.fn() };
      const mockDatabase = {
        query: jest.fn().mockResolvedValue({ id: 1, name: 'John' }),
      };

      const service = new UserService(mockLogger, mockDatabase);
      const user = await service.getUser(1);

      expect(user.name).toBe('John');
      expect(mockLogger.log).toHaveBeenCalledWith('Getting user 1');
      expect(mockDatabase.query).toHaveBeenCalled();
    });
  });

  // Property injection
  describe('Property Injection', () => {
    interface IEmailService {
      send(to: string, subject: string): Promise<boolean>;
    }

    class NotificationService {
      emailService!: IEmailService;

      async notify(email: string, message: string): Promise<boolean> {
        return this.emailService.send(email, message);
      }
    }

    test('sets property dependencies', async () => {
      const service = new NotificationService();
      service.emailService = {
        send: jest.fn().mockResolvedValue(true),
      };

      const result = await service.notify('user@example.com', 'Hello');

      expect(result).toBe(true);
      expect(service.emailService.send).toHaveBeenCalledWith(
        'user@example.com',
        'Hello'
      );
    });
  });

  // Method injection
  describe('Method Injection', () => {
    interface IValidator {
      validate(data: any): boolean;
    }

    class DataProcessor {
      process(data: any, validator: IValidator): boolean {
        if (!validator.validate(data)) {
          return false;
        }
        // Process data
        return true;
      }
    }

    test('injects dependencies via method', () => {
      const processor = new DataProcessor();
      const mockValidator = { validate: jest.fn().mockReturnValue(true) };

      const result = processor.process({ test: 'data' }, mockValidator);

      expect(result).toBe(true);
      expect(mockValidator.validate).toHaveBeenCalledWith({ test: 'data' });
    });
  });

  // Factory pattern injection
  describe('Factory Pattern', () => {
    interface ICache {
      get(key: string): any;
      set(key: string, value: any): void;
    }

    type CacheFactory = () => ICache;

    class CacheManager {
      constructor(private cacheFactory: CacheFactory) {}

      getCache(): ICache {
        return this.cacheFactory();
      }
    }

    test('uses factory to create dependencies', () => {
      const mockCache = {
        get: jest.fn(),
        set: jest.fn(),
      };

      const mockFactory = jest.fn(() => mockCache);
      const manager = new CacheManager(mockFactory);

      const cache = manager.getCache();
      cache.set('key', 'value');

      expect(mockFactory).toHaveBeenCalled();
      expect(mockCache.set).toHaveBeenCalledWith('key', 'value');
    });
  });

  // Service locator pattern
  describe('Service Locator', () => {
    class ServiceLocator {
      private services = new Map<string, any>();

      register<T>(name: string, service: T): void {
        this.services.set(name, service);
      }

      resolve<T>(name: string): T {
        if (!this.services.has(name)) {
          throw new Error(`Service ${name} not found`);
        }
        return this.services.get(name);
      }
    }

    class Application {
      constructor(private locator: ServiceLocator) {}

      run(): string {
        const logger = this.locator.resolve<{ log: (msg: string) => void }>('logger');
        logger.log('App started');
        return 'running';
      }
    }

    test('resolves services from locator', () => {
      const locator = new ServiceLocator();
      const mockLogger = { log: jest.fn() };
      locator.register('logger', mockLogger);

      const app = new Application(locator);
      const result = app.run();

      expect(result).toBe('running');
      expect(mockLogger.log).toHaveBeenCalledWith('App started');
    });

    test('throws when service not found', () => {
      const locator = new ServiceLocator();
      const app = new Application(locator);

      expect(() => app.run()).toThrow('Service logger not found');
    });
  });

  // Interface segregation
  describe('Interface Segregation', () => {
    interface IReader {
      read(): string;
    }

    interface IWriter {
      write(data: string): void;
    }

    class FileProcessor {
      constructor(
        private reader: IReader,
        private writer: IWriter
      ) {}

      process(): void {
        const data = this.reader.read();
        this.writer.write(data.toUpperCase());
      }
    }

    test('uses segregated interfaces', () => {
      const mockReader = { read: jest.fn().mockReturnValue('hello') };
      const mockWriter = { write: jest.fn() };

      const processor = new FileProcessor(mockReader, mockWriter);
      processor.process();

      expect(mockReader.read).toHaveBeenCalled();
      expect(mockWriter.write).toHaveBeenCalledWith('HELLO');
    });
  });

  // Optional dependencies
  describe('Optional Dependencies', () => {
    interface IAnalytics {
      track(event: string): void;
    }

    class UserController {
      constructor(
        private analytics?: IAnalytics
      ) {}

      createUser(name: string): { name: string } {
        const user = { name };
        this.analytics?.track('user_created');
        return user;
      }
    }

    test('works without optional dependency', () => {
      const controller = new UserController();
      const user = controller.createUser('John');

      expect(user.name).toBe('John');
    });

    test('uses optional dependency when provided', () => {
      const mockAnalytics = { track: jest.fn() };
      const controller = new UserController(mockAnalytics);
      const user = controller.createUser('John');

      expect(user.name).toBe('John');
      expect(mockAnalytics.track).toHaveBeenCalledWith('user_created');
    });
  });

  // Circular dependency resolution
  describe('Circular Dependencies', () => {
    interface ServiceA {
      getName(): string;
      setServiceB(service: ServiceB): void;
    }

    interface ServiceB {
      getName(): string;
      setServiceA(service: ServiceA): void;
    }

    class ConcreteServiceA implements ServiceA {
      private serviceB?: ServiceB;

      getName(): string {
        return 'ServiceA';
      }

      setServiceB(service: ServiceB): void {
        this.serviceB = service;
      }

      callServiceB(): string {
        return this.serviceB?.getName() || 'no B';
      }
    }

    class ConcreteServiceB implements ServiceB {
      private serviceA?: ServiceA;

      getName(): string {
        return 'ServiceB';
      }

      setServiceA(service: ServiceA): void {
        this.serviceA = service;
      }

      callServiceA(): string {
        return this.serviceA?.getName() || 'no A';
      }
    }

    test('resolves circular dependencies', () => {
      const serviceA = new ConcreteServiceA();
      const serviceB = new ConcreteServiceB();

      serviceA.setServiceB(serviceB);
      serviceB.setServiceA(serviceA);

      expect(serviceA.callServiceB()).toBe('ServiceB');
      expect(serviceB.callServiceA()).toBe('ServiceA');
    });
  });

  // Scoped dependencies
  describe('Scoped Dependencies', () => {
    interface IRequestContext {
      requestId: string;
    }

    class RequestScopedService {
      constructor(private context: IRequestContext) {}

      getRequestId(): string {
        return this.context.requestId;
      }
    }

    class ServiceFactory {
      createService(requestId: string): RequestScopedService {
        return new RequestScopedService({ requestId });
      }
    }

    test('creates scoped instances', () => {
      const factory = new ServiceFactory();

      const service1 = factory.createService('req-1');
      const service2 = factory.createService('req-2');

      expect(service1.getRequestId()).toBe('req-1');
      expect(service2.getRequestId()).toBe('req-2');
    });
  });

  // Dependency lifetime management
  describe('Dependency Lifetime', () => {
    class SingletonService {
      private static instance: SingletonService;
      public callCount = 0;

      static getInstance(): SingletonService {
        if (!this.instance) {
          this.instance = new SingletonService();
        }
        return this.instance;
      }

      call(): void {
        this.callCount++;
      }
    }

    class TransientService {
      public callCount = 0;

      call(): void {
        this.callCount++;
      }
    }

    test('singleton maintains state', () => {
      const instance1 = SingletonService.getInstance();
      const instance2 = SingletonService.getInstance();

      instance1.call();
      instance2.call();

      expect(instance1.callCount).toBe(2);
      expect(instance2.callCount).toBe(2);
      expect(instance1).toBe(instance2);
    });

    test('transient creates new instances', () => {
      const instance1 = new TransientService();
      const instance2 = new TransientService();

      instance1.call();
      instance2.call();

      expect(instance1.callCount).toBe(1);
      expect(instance2.callCount).toBe(1);
      expect(instance1).not.toBe(instance2);
    });
  });
});
