// Mock Data Generators (Fixed)
// Generate realistic test data

export class MockDataGenerator {
  static user() {
    const firstNames = ['John', 'Jane', 'Bob', 'Alice', 'Charlie'];
    const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'];
    const first = firstNames[Math.floor(Math.random() * firstNames.length)];
    const last = lastNames[Math.floor(Math.random() * lastNames.length)];

    return {
      id: Math.floor(Math.random() * 10000),
      name: `${first} ${last}`,
      email: this.email(),
      age: Math.floor(Math.random() * 80) + 18,
      createdAt: new Date(),
    };
  }

  static email(): string {
    const id = Math.random().toString(36).substr(2, 9);
    return `user${id}@example.com`;
  }

  static phone(): string {
    return `+1${Math.floor(Math.random() * 9000000000) + 1000000000}`;
  }

  static address() {
    const cities = ['New York', 'Los Angeles', 'Chicago'];
    const states = ['NY', 'CA', 'IL'];
    const idx = Math.floor(Math.random() * 3);

    return {
      street: `${Math.floor(Math.random() * 9999) + 1} Main St`,
      city: cities[idx],
      state: states[idx],
      zip: Math.floor(Math.random() * 90000) + 10000,
    };
  }

  static product() {
    return {
      id: Math.floor(Math.random() * 10000),
      name: `Product ${Math.floor(Math.random() * 100)}`,
      price: Math.floor(Math.random() * 10000) / 100,
      inStock: Math.random() > 0.3,
    };
  }
}
