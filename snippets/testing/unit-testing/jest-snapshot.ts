// Jest Snapshot Testing
// Comprehensive snapshot testing examples

interface User {
  id: number;
  name: string;
  email: string;
  createdAt: Date;
}

class UserFormatter {
  static formatUser(user: User): object {
    return {
      id: user.id,
      name: user.name,
      email: user.email,
      createdAt: user.createdAt.toISOString(),
    };
  }

  static formatUserList(users: User[]): object[] {
    return users.map(this.formatUser);
  }
}

describe('Snapshot Testing', () => {
  test('matches user snapshot', () => {
    const user: User = {
      id: 1,
      name: 'John Doe',
      email: 'john@example.com',
      createdAt: new Date('2024-01-01'),
    };

    expect(UserFormatter.formatUser(user)).toMatchSnapshot();
  });

  test('matches inline snapshot', () => {
    const data = { foo: 'bar', baz: 42 };
    expect(data).toMatchInlineSnapshot(`
      {
        "baz": 42,
        "foo": "bar",
      }
    `);
  });

  test('property matchers', () => {
    const user: User = {
      id: 1,
      name: 'Jane Doe',
      email: 'jane@example.com',
      createdAt: new Date(),
    };

    expect(UserFormatter.formatUser(user)).toMatchSnapshot({
      createdAt: expect.any(String),
    });
  });

  test('snapshot with dynamic data', () => {
    const users: User[] = [
      {
        id: 1,
        name: 'John',
        email: 'john@example.com',
        createdAt: new Date('2024-01-01'),
      },
      {
        id: 2,
        name: 'Jane',
        email: 'jane@example.com',
        createdAt: new Date('2024-01-02'),
      },
    ];

    expect(UserFormatter.formatUserList(users)).toMatchSnapshot();
  });
});

// Component Snapshot Testing (React example)
describe('Component Snapshots', () => {
  test('renders component', () => {
    const component = {
      type: 'div',
      props: {
        className: 'container',
        children: 'Hello World',
      },
    };

    expect(component).toMatchSnapshot();
  });

  test('renders with custom serializer', () => {
    const tree = {
      node: 'div',
      attributes: { class: 'container' },
      children: ['Hello World'],
    };

    expect(tree).toMatchSnapshot();
  });
});
