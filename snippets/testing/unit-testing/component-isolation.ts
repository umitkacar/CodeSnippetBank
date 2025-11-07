// Component Isolation Testing
// Patterns for testing components in isolation

describe('Component Isolation', () => {
  // Service isolation
  describe('Service Isolation', () => {
    interface ApiClient {
      get(url: string): Promise<any>;
      post(url: string, data: any): Promise<any>;
    }

    class UserService {
      constructor(private apiClient: ApiClient) {}

      async getUser(id: number) {
        return this.apiClient.get(`/users/${id}`);
      }

      async createUser(data: any) {
        return this.apiClient.post('/users', data);
      }
    }

    test('isolates service from API client', async () => {
      const mockApiClient = {
        get: jest.fn().mockResolvedValue({ id: 1, name: 'John' }),
        post: jest.fn().mockResolvedValue({ id: 1, name: 'John' }),
      };

      const service = new UserService(mockApiClient);
      const user = await service.getUser(1);

      expect(user.name).toBe('John');
      expect(mockApiClient.get).toHaveBeenCalledWith('/users/1');
    });
  });

  // Module isolation
  describe('Module Isolation', () => {
    // Simulated module dependencies
    const logger = {
      log: jest.fn(),
      error: jest.fn(),
    };

    const database = {
      query: jest.fn(),
      execute: jest.fn(),
    };

    class OrderService {
      constructor(
        private logger: typeof logger,
        private database: typeof database
      ) {}

      async createOrder(orderData: any) {
        this.logger.log('Creating order');
        await this.database.execute('INSERT INTO orders', orderData);
        this.logger.log('Order created');
        return { id: 1, ...orderData };
      }
    }

    beforeEach(() => {
      jest.clearAllMocks();
    });

    test('isolates from all dependencies', async () => {
      const service = new OrderService(logger, database);
      database.execute.mockResolvedValue(true);

      const order = await service.createOrder({ item: 'Product' });

      expect(order.item).toBe('Product');
      expect(logger.log).toHaveBeenCalledTimes(2);
      expect(database.execute).toHaveBeenCalled();
    });
  });

  // Component boundary testing
  describe('Component Boundaries', () => {
    interface Validator {
      validate(data: any): boolean;
    }

    interface Formatter {
      format(data: any): string;
    }

    class DataProcessor {
      constructor(
        private validator: Validator,
        private formatter: Formatter
      ) {}

      process(data: any): string {
        if (!this.validator.validate(data)) {
          throw new Error('Invalid data');
        }
        return this.formatter.format(data);
      }
    }

    test('tests only processor logic', () => {
      const mockValidator = {
        validate: jest.fn().mockReturnValue(true),
      };

      const mockFormatter = {
        format: jest.fn().mockReturnValue('formatted'),
      };

      const processor = new DataProcessor(mockValidator, mockFormatter);
      const result = processor.process({ test: 'data' });

      expect(result).toBe('formatted');
      expect(mockValidator.validate).toHaveBeenCalled();
      expect(mockFormatter.format).toHaveBeenCalled();
    });

    test('handles validation failure', () => {
      const mockValidator = {
        validate: jest.fn().mockReturnValue(false),
      };

      const mockFormatter = {
        format: jest.fn(),
      };

      const processor = new DataProcessor(mockValidator, mockFormatter);

      expect(() => processor.process({ test: 'data' })).toThrow('Invalid data');
      expect(mockFormatter.format).not.toHaveBeenCalled();
    });
  });

  // Pure function isolation
  describe('Pure Function Isolation', () => {
    function calculateTotal(items: Array<{ price: number; quantity: number }>): number {
      return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
    }

    function applyDiscount(total: number, discountPercent: number): number {
      return total * (1 - discountPercent / 100);
    }

    function calculateFinalPrice(
      items: Array<{ price: number; quantity: number }>,
      discountPercent: number
    ): number {
      const total = calculateTotal(items);
      return applyDiscount(total, discountPercent);
    }

    test('calculateTotal in isolation', () => {
      const items = [
        { price: 10, quantity: 2 },
        { price: 5, quantity: 3 },
      ];
      expect(calculateTotal(items)).toBe(35);
    });

    test('applyDiscount in isolation', () => {
      expect(applyDiscount(100, 10)).toBe(90);
      expect(applyDiscount(50, 20)).toBe(40);
    });

    test('calculateFinalPrice composition', () => {
      const items = [{ price: 10, quantity: 2 }];
      expect(calculateFinalPrice(items, 10)).toBe(18);
    });
  });

  // State isolation
  describe('State Isolation', () => {
    class StateManager {
      private state: Map<string, any> = new Map();

      set(key: string, value: any): void {
        this.state.set(key, value);
      }

      get(key: string): any {
        return this.state.get(key);
      }

      clear(): void {
        this.state.clear();
      }
    }

    let manager: StateManager;

    beforeEach(() => {
      manager = new StateManager();
    });

    afterEach(() => {
      manager.clear();
    });

    test('isolated state test 1', () => {
      manager.set('key', 'value1');
      expect(manager.get('key')).toBe('value1');
    });

    test('isolated state test 2', () => {
      // State is fresh, not affected by previous test
      expect(manager.get('key')).toBeUndefined();
      manager.set('key', 'value2');
      expect(manager.get('key')).toBe('value2');
    });
  });

  // External service isolation
  describe('External Service Isolation', () => {
    interface PaymentGateway {
      charge(amount: number): Promise<boolean>;
    }

    interface EmailService {
      sendReceipt(email: string, amount: number): Promise<void>;
    }

    class CheckoutService {
      constructor(
        private payment: PaymentGateway,
        private email: EmailService
      ) {}

      async processCheckout(email: string, amount: number): Promise<boolean> {
        const charged = await this.payment.charge(amount);
        if (charged) {
          await this.email.sendReceipt(email, amount);
          return true;
        }
        return false;
      }
    }

    test('isolates from payment gateway', async () => {
      const mockPayment = {
        charge: jest.fn().mockResolvedValue(true),
      };

      const mockEmail = {
        sendReceipt: jest.fn().mockResolvedValue(undefined),
      };

      const service = new CheckoutService(mockPayment, mockEmail);
      const result = await service.processCheckout('user@example.com', 100);

      expect(result).toBe(true);
      expect(mockPayment.charge).toHaveBeenCalledWith(100);
      expect(mockEmail.sendReceipt).toHaveBeenCalledWith('user@example.com', 100);
    });

    test('handles payment failure', async () => {
      const mockPayment = {
        charge: jest.fn().mockResolvedValue(false),
      };

      const mockEmail = {
        sendReceipt: jest.fn(),
      };

      const service = new CheckoutService(mockPayment, mockEmail);
      const result = await service.processCheckout('user@example.com', 100);

      expect(result).toBe(false);
      expect(mockEmail.sendReceipt).not.toHaveBeenCalled();
    });
  });

  // Time isolation
  describe('Time Isolation', () => {
    class TimeService {
      now(): Date {
        return new Date();
      }
    }

    class Scheduler {
      constructor(private timeService: TimeService) {}

      scheduleTask(delayMs: number): Date {
        const now = this.timeService.now();
        return new Date(now.getTime() + delayMs);
      }
    }

    test('isolates from system time', () => {
      const mockTimeService = {
        now: jest.fn().mockReturnValue(new Date('2024-01-01T00:00:00Z')),
      };

      const scheduler = new Scheduler(mockTimeService);
      const scheduled = scheduler.scheduleTask(1000);

      expect(scheduled.toISOString()).toBe('2024-01-01T00:00:01.000Z');
    });
  });

  // Random isolation
  describe('Random Isolation', () => {
    interface RandomGenerator {
      next(): number;
    }

    class GameLogic {
      constructor(private random: RandomGenerator) {}

      rollDice(): number {
        return Math.floor(this.random.next() * 6) + 1;
      }
    }

    test('isolates from randomness', () => {
      const mockRandom = {
        next: jest.fn().mockReturnValue(0.5),
      };

      const game = new GameLogic(mockRandom);
      const roll = game.rollDice();

      expect(roll).toBe(4); // floor(0.5 * 6) + 1
    });

    test('tests different random outcomes', () => {
      const mockRandom = {
        next: jest.fn().mockReturnValueOnce(0).mockReturnValueOnce(0.99),
      };

      const game = new GameLogic(mockRandom);

      expect(game.rollDice()).toBe(1); // Minimum
      expect(game.rollDice()).toBe(6); // Maximum
    });
  });
});
