// Service Integration Testing
// Testing interactions between multiple services

describe('Service Integration Testing', () => {
  // Service interfaces
  interface UserService {
    getUser(id: number): Promise<{ id: number; name: string }>;
    createUser(data: any): Promise<{ id: number; name: string }>;
  }

  interface EmailService {
    sendWelcomeEmail(email: string): Promise<boolean>;
  }

  interface NotificationService {
    notify(userId: number, message: string): Promise<void>;
  }

  // Implementation
  class UserServiceImpl implements UserService {
    async getUser(id: number) {
      return { id, name: `User ${id}` };
    }

    async createUser(data: any) {
      return { id: 1, ...data };
    }
  }

  class EmailServiceImpl implements EmailService {
    async sendWelcomeEmail(email: string) {
      return true;
    }
  }

  class NotificationServiceImpl implements NotificationService {
    async notify(userId: number, message: string) {
      // Send notification
    }
  }

  // Integration service
  class UserRegistrationService {
    constructor(
      private userService: UserService,
      private emailService: EmailService,
      private notificationService: NotificationService
    ) {}

    async registerUser(name: string, email: string) {
      const user = await this.userService.createUser({ name, email });
      await this.emailService.sendWelcomeEmail(email);
      await this.notificationService.notify(user.id, 'Welcome!');
      return user;
    }
  }

  describe('User Registration Flow', () => {
    let registrationService: UserRegistrationService;

    beforeEach(() => {
      const userService = new UserServiceImpl();
      const emailService = new EmailServiceImpl();
      const notificationService = new NotificationServiceImpl();

      registrationService = new UserRegistrationService(
        userService,
        emailService,
        notificationService
      );
    });

    test('registers user with all services', async () => {
      const user = await registrationService.registerUser(
        'John',
        'john@example.com'
      );

      expect(user).toBeDefined();
      expect(user.name).toBe('John');
    });
  });
});
