// Test Doubles Patterns
// Comprehensive examples of test doubles: mocks, stubs, fakes, spies, dummies

// Interfaces for testing
interface User {
  id: number;
  name: string;
  email: string;
}

interface Database {
  save(data: any): Promise<boolean>;
  findById(id: number): Promise<User | null>;
  findAll(): Promise<User[]>;
  delete(id: number): Promise<boolean>;
}

interface EmailService {
  sendEmail(to: string, subject: string, body: string): Promise<boolean>;
}

interface Logger {
  log(message: string): void;
  error(message: string): void;
}

// 1. DUMMY - Objects passed around but never used
describe('Dummy Test Doubles', () => {
  class DummyLogger implements Logger {
    log(message: string): void {
      // Intentionally empty - never used
    }
    error(message: string): void {
      // Intentionally empty - never used
    }
  }

  class UserRegistration {
    constructor(private logger: Logger) {}

    register(name: string): User {
      // Logger is required but not used in this path
      return { id: 1, name, email: `${name}@example.com` };
    }
  }

  test('uses dummy logger', () => {
    const dummyLogger = new DummyLogger();
    const registration = new UserRegistration(dummyLogger);

    const user = registration.register('John');

    expect(user.name).toBe('John');
  });
});

// 2. STUB - Provides predetermined responses
describe('Stub Test Doubles', () => {
  class StubDatabase implements Database {
    async save(data: any): Promise<boolean> {
      return true; // Always succeeds
    }

    async findById(id: number): Promise<User | null> {
      // Predetermined response
      return {
        id,
        name: 'Stub User',
        email: 'stub@example.com',
      };
    }

    async findAll(): Promise<User[]> {
      // Fixed response
      return [
        { id: 1, name: 'User 1', email: 'user1@example.com' },
        { id: 2, name: 'User 2', email: 'user2@example.com' },
      ];
    }

    async delete(id: number): Promise<boolean> {
      return true;
    }
  }

  class UserService {
    constructor(private db: Database) {}

    async getUser(id: number): Promise<User | null> {
      return this.db.findById(id);
    }

    async getAllUsers(): Promise<User[]> {
      return this.db.findAll();
    }
  }

  test('uses stub database', async () => {
    const stubDb = new StubDatabase();
    const service = new UserService(stubDb);

    const user = await service.getUser(1);

    expect(user).toBeDefined();
    expect(user?.name).toBe('Stub User');
  });

  test('stub returns fixed list', async () => {
    const stubDb = new StubDatabase();
    const service = new UserService(stubDb);

    const users = await service.getAllUsers();

    expect(users).toHaveLength(2);
  });
});

// 3. FAKE - Working implementation with shortcuts
describe('Fake Test Doubles', () => {
  class FakeDatabase implements Database {
    private storage: Map<number, User> = new Map();
    private nextId: number = 1;

    async save(data: any): Promise<boolean> {
      const user = { ...data, id: this.nextId++ };
      this.storage.set(user.id, user);
      return true;
    }

    async findById(id: number): Promise<User | null> {
      return this.storage.get(id) || null;
    }

    async findAll(): Promise<User[]> {
      return Array.from(this.storage.values());
    }

    async delete(id: number): Promise<boolean> {
      return this.storage.delete(id);
    }
  }

  class UserRepository {
    constructor(private db: Database) {}

    async createUser(name: string, email: string): Promise<User> {
      const user = { id: 0, name, email };
      await this.db.save(user);
      return user;
    }

    async getUser(id: number): Promise<User | null> {
      return this.db.findById(id);
    }

    async deleteUser(id: number): Promise<boolean> {
      return this.db.delete(id);
    }
  }

  test('fake database stores data', async () => {
    const fakeDb = new FakeDatabase();
    const repo = new UserRepository(fakeDb);

    await repo.createUser('John', 'john@example.com');
    await repo.createUser('Jane', 'jane@example.com');

    const users = await fakeDb.findAll();
    expect(users).toHaveLength(2);
  });

  test('fake database retrieves stored data', async () => {
    const fakeDb = new FakeDatabase();
    await fakeDb.save({ name: 'John', email: 'john@example.com' });

    const user = await fakeDb.findById(1);

    expect(user).toBeDefined();
    expect(user?.name).toBe('John');
  });

  test('fake database deletes data', async () => {
    const fakeDb = new FakeDatabase();
    await fakeDb.save({ name: 'John', email: 'john@example.com' });

    const deleted = await fakeDb.delete(1);
    const user = await fakeDb.findById(1);

    expect(deleted).toBe(true);
    expect(user).toBeNull();
  });
});

// 4. MOCK - Pre-programmed with expectations
describe('Mock Test Doubles', () => {
  class MockEmailService implements EmailService {
    public calls: Array<{ to: string; subject: string; body: string }> = [];

    async sendEmail(to: string, subject: string, body: string): Promise<boolean> {
      this.calls.push({ to, subject, body });
      return true;
    }

    verify(expectedCalls: number): boolean {
      return this.calls.length === expectedCalls;
    }

    verifySentTo(email: string): boolean {
      return this.calls.some((call) => call.to === email);
    }
  }

  class NotificationService {
    constructor(private emailService: EmailService) {}

    async notifyUser(user: User, message: string): Promise<void> {
      await this.emailService.sendEmail(
        user.email,
        'Notification',
        message
      );
    }

    async notifyMultipleUsers(users: User[], message: string): Promise<void> {
      for (const user of users) {
        await this.emailService.sendEmail(
          user.email,
          'Notification',
          message
        );
      }
    }
  }

  test('mock verifies interactions', async () => {
    const mockEmail = new MockEmailService();
    const service = new NotificationService(mockEmail);

    await service.notifyUser(
      { id: 1, name: 'John', email: 'john@example.com' },
      'Hello'
    );

    expect(mockEmail.verify(1)).toBe(true);
    expect(mockEmail.verifySentTo('john@example.com')).toBe(true);
  });

  test('mock tracks multiple calls', async () => {
    const mockEmail = new MockEmailService();
    const service = new NotificationService(mockEmail);

    const users = [
      { id: 1, name: 'John', email: 'john@example.com' },
      { id: 2, name: 'Jane', email: 'jane@example.com' },
    ];

    await service.notifyMultipleUsers(users, 'Update');

    expect(mockEmail.verify(2)).toBe(true);
    expect(mockEmail.calls[0].to).toBe('john@example.com');
    expect(mockEmail.calls[1].to).toBe('jane@example.com');
  });
});

// 5. SPY - Records information about calls
describe('Spy Test Doubles', () => {
  class SpyLogger implements Logger {
    public logCalls: string[] = [];
    public errorCalls: string[] = [];

    log(message: string): void {
      this.logCalls.push(message);
      console.log(message); // Still performs real action
    }

    error(message: string): void {
      this.errorCalls.push(message);
      console.error(message); // Still performs real action
    }

    getLogCount(): number {
      return this.logCalls.length;
    }

    getErrorCount(): number {
      return this.errorCalls.length;
    }

    wasLogged(message: string): boolean {
      return this.logCalls.includes(message);
    }
  }

  class ApplicationService {
    constructor(private logger: Logger) {}

    processRequest(data: any): void {
      this.logger.log('Processing request');
      // Process logic
      this.logger.log('Request processed successfully');
    }

    handleError(error: Error): void {
      this.logger.error(`Error: ${error.message}`);
    }
  }

  test('spy records log calls', () => {
    const spyLogger = new SpyLogger();
    const service = new ApplicationService(spyLogger);

    service.processRequest({});

    expect(spyLogger.getLogCount()).toBe(2);
    expect(spyLogger.wasLogged('Processing request')).toBe(true);
  });

  test('spy records error calls', () => {
    const spyLogger = new SpyLogger();
    const service = new ApplicationService(spyLogger);

    service.handleError(new Error('Test error'));

    expect(spyLogger.getErrorCount()).toBe(1);
    expect(spyLogger.errorCalls[0]).toContain('Test error');
  });
});

// Combining Test Doubles
describe('Combined Test Doubles', () => {
  interface PaymentGateway {
    charge(amount: number): Promise<boolean>;
  }

  class FakePaymentGateway implements PaymentGateway {
    public transactions: number[] = [];

    async charge(amount: number): Promise<boolean> {
      this.transactions.push(amount);
      return amount > 0;
    }
  }

  class OrderService {
    constructor(
      private db: Database,
      private payment: PaymentGateway,
      private email: EmailService,
      private logger: Logger
    ) {}

    async placeOrder(user: User, amount: number): Promise<boolean> {
      this.logger.log(`Processing order for ${user.name}`);

      const charged = await this.payment.charge(amount);
      if (!charged) {
        this.logger.error('Payment failed');
        return false;
      }

      await this.db.save({ userId: user.id, amount });
      await this.email.sendEmail(user.email, 'Order Confirmation', 'Thank you');

      this.logger.log('Order completed');
      return true;
    }
  }

  test('combines multiple test doubles', async () => {
    const fakeDb = new FakeDatabase();
    const fakePayment = new FakePaymentGateway();
    const mockEmail = new MockEmailService();
    const spyLogger = new SpyLogger();

    const service = new OrderService(fakeDb, fakePayment, mockEmail, spyLogger);

    const user = { id: 1, name: 'John', email: 'john@example.com' };
    const result = await service.placeOrder(user, 100);

    expect(result).toBe(true);
    expect(fakePayment.transactions).toContain(100);
    expect(mockEmail.verifySentTo('john@example.com')).toBe(true);
    expect(spyLogger.wasLogged('Order completed')).toBe(true);
  });
});
