// Test Fixtures for Integration Testing
// Reusable test data and setup

export class TestFixtures {
  static users = {
    john: { id: 1, name: 'John Doe', email: 'john@example.com', role: 'user' },
    jane: { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'admin' },
    bob: { id: 3, name: 'Bob Johnson', email: 'bob@example.com', role: 'user' },
  };

  static posts = {
    post1: { id: 1, title: 'First Post', content: 'Content 1', authorId: 1 },
    post2: { id: 2, title: 'Second Post', content: 'Content 2', authorId: 2 },
  };

  static comments = {
    comment1: { id: 1, content: 'Great post!', postId: 1, authorId: 2 },
    comment2: { id: 2, content: 'Thanks!', postId: 1, authorId: 1 },
  };

  static createUser(overrides?: Partial<typeof TestFixtures.users.john>) {
    return {
      ...TestFixtures.users.john,
      ...overrides,
    };
  }

  static createPost(overrides?: Partial<typeof TestFixtures.posts.post1>) {
    return {
      ...TestFixtures.posts.post1,
      ...overrides,
    };
  }
}

describe('Using Test Fixtures', () => {
  test('uses predefined user fixture', () => {
    const user = TestFixtures.users.john;
    expect(user.name).toBe('John Doe');
  });

  test('creates custom user from fixture', () => {
    const customUser = TestFixtures.createUser({ name: 'Custom User' });
    expect(customUser.name).toBe('Custom User');
    expect(customUser.email).toBe('john@example.com'); // Inherited
  });
});
