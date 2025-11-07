// Factory Patterns for Testing
// Create test objects with factory pattern

export class UserFactory {
  private defaults = {
    id: 1,
    name: 'Test User',
    email: 'test@example.com',
    role: 'user',
    active: true,
  };

  static create(overrides?: Partial<typeof UserFactory.prototype.defaults>) {
    return new UserFactory().build(overrides);
  }

  build(overrides?: Partial<typeof this.defaults>) {
    return { ...this.defaults, ...overrides, id: Math.floor(Math.random() * 10000) };
  }

  buildList(count: number, overrides?: Partial<typeof this.defaults>) {
    return Array.from({ length: count }, () => this.build(overrides));
  }
}

export class PostFactory {
  static create(overrides?: any) {
    return {
      id: Math.floor(Math.random() * 10000),
      title: 'Test Post',
      content: 'Test content',
      authorId: 1,
      published: false,
      createdAt: new Date(),
      ...overrides,
    };
  }

  static createPublished(overrides?: any) {
    return this.create({ published: true, ...overrides });
  }
}

describe('Factory Patterns', () => {
  test('creates user with defaults', () => {
    const user = UserFactory.create();
    expect(user.name).toBe('Test User');
    expect(user.role).toBe('user');
  });

  test('creates user with overrides', () => {
    const user = UserFactory.create({ name: 'Custom User', role: 'admin' });
    expect(user.name).toBe('Custom User');
    expect(user.role).toBe('admin');
  });

  test('creates list of users', () => {
    const factory = new UserFactory();
    const users = factory.buildList(5);
    expect(users).toHaveLength(5);
  });
});
