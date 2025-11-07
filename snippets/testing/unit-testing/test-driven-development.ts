// Test-Driven Development (TDD) Examples
// Red-Green-Refactor cycle demonstrations

// Example 1: Simple function TDD
describe('TDD Example: String Utilities', () => {
  // RED: Write failing test first
  describe('capitalize', () => {
    test('capitalizes first letter', () => {
      expect(capitalize('hello')).toBe('Hello');
    });

    test('handles empty string', () => {
      expect(capitalize('')).toBe('');
    });

    test('handles already capitalized', () => {
      expect(capitalize('Hello')).toBe('Hello');
    });

    test('handles single character', () => {
      expect(capitalize('a')).toBe('A');
    });
  });
});

// GREEN: Implement minimum code to pass
function capitalize(str: string): string {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

// REFACTOR: Improve implementation
function capitalizeRefactored(str: string): string {
  return str ? str.charAt(0).toUpperCase() + str.slice(1).toLowerCase() : '';
}

// Example 2: Class TDD
describe('TDD Example: Shopping Cart', () => {
  let cart: ShoppingCart;

  beforeEach(() => {
    cart = new ShoppingCart();
  });

  // RED: Write tests first
  describe('addItem', () => {
    test('adds item to cart', () => {
      cart.addItem({ id: 1, name: 'Product 1', price: 10 });
      expect(cart.getItemCount()).toBe(1);
    });

    test('adds multiple items', () => {
      cart.addItem({ id: 1, name: 'Product 1', price: 10 });
      cart.addItem({ id: 2, name: 'Product 2', price: 20 });
      expect(cart.getItemCount()).toBe(2);
    });
  });

  describe('removeItem', () => {
    test('removes item from cart', () => {
      cart.addItem({ id: 1, name: 'Product 1', price: 10 });
      cart.removeItem(1);
      expect(cart.getItemCount()).toBe(0);
    });

    test('does nothing if item not found', () => {
      cart.addItem({ id: 1, name: 'Product 1', price: 10 });
      cart.removeItem(999);
      expect(cart.getItemCount()).toBe(1);
    });
  });

  describe('getTotal', () => {
    test('calculates total price', () => {
      cart.addItem({ id: 1, name: 'Product 1', price: 10 });
      cart.addItem({ id: 2, name: 'Product 2', price: 20 });
      expect(cart.getTotal()).toBe(30);
    });

    test('returns 0 for empty cart', () => {
      expect(cart.getTotal()).toBe(0);
    });
  });

  describe('clear', () => {
    test('clears all items', () => {
      cart.addItem({ id: 1, name: 'Product 1', price: 10 });
      cart.addItem({ id: 2, name: 'Product 2', price: 20 });
      cart.clear();
      expect(cart.getItemCount()).toBe(0);
      expect(cart.getTotal()).toBe(0);
    });
  });

  describe('getItems', () => {
    test('returns all items', () => {
      const item1 = { id: 1, name: 'Product 1', price: 10 };
      const item2 = { id: 2, name: 'Product 2', price: 20 };
      cart.addItem(item1);
      cart.addItem(item2);
      expect(cart.getItems()).toEqual([item1, item2]);
    });
  });
});

// GREEN: Implement the class
interface CartItem {
  id: number;
  name: string;
  price: number;
}

class ShoppingCart {
  private items: CartItem[] = [];

  addItem(item: CartItem): void {
    this.items.push(item);
  }

  removeItem(id: number): void {
    this.items = this.items.filter((item) => item.id !== id);
  }

  getItemCount(): number {
    return this.items.length;
  }

  getTotal(): number {
    return this.items.reduce((sum, item) => sum + item.price, 0);
  }

  clear(): void {
    this.items = [];
  }

  getItems(): CartItem[] {
    return [...this.items];
  }
}

// Example 3: Async function TDD
describe('TDD Example: API Client', () => {
  let client: ApiClient;

  beforeEach(() => {
    client = new ApiClient('https://api.example.com');
  });

  // RED: Write async tests first
  describe('get', () => {
    test('fetches data successfully', async () => {
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ data: 'test' }),
      } as Response);

      const result = await client.get('/users');
      expect(result).toEqual({ data: 'test' });
    });

    test('throws on error response', async () => {
      global.fetch = jest.fn().mockResolvedValue({
        ok: false,
        status: 404,
      } as Response);

      await expect(client.get('/users')).rejects.toThrow('Request failed: 404');
    });
  });

  describe('post', () => {
    test('posts data successfully', async () => {
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ id: 1, name: 'John' }),
      } as Response);

      const result = await client.post('/users', { name: 'John' });
      expect(result).toEqual({ id: 1, name: 'John' });
    });
  });
});

// GREEN: Implement API client
class ApiClient {
  constructor(private baseUrl: string) {}

  async get(endpoint: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}${endpoint}`);
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return response.json();
  }

  async post(endpoint: string, data: any): Promise<any> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return response.json();
  }
}

// Example 4: Complex business logic TDD
describe('TDD Example: Order Processing', () => {
  let processor: OrderProcessor;

  beforeEach(() => {
    processor = new OrderProcessor();
  });

  describe('calculateDiscount', () => {
    test('applies no discount for small orders', () => {
      expect(processor.calculateDiscount(50)).toBe(0);
    });

    test('applies 10% discount for orders over 100', () => {
      expect(processor.calculateDiscount(100)).toBe(10);
    });

    test('applies 20% discount for orders over 500', () => {
      expect(processor.calculateDiscount(500)).toBe(100);
    });

    test('applies 30% discount for orders over 1000', () => {
      expect(processor.calculateDiscount(1000)).toBe(300);
    });
  });

  describe('processOrder', () => {
    test('processes order with discount', () => {
      const result = processor.processOrder(150, 'premium');
      expect(result.subtotal).toBe(150);
      expect(result.discount).toBe(15);
      expect(result.total).toBe(135);
    });

    test('adds shipping for non-premium', () => {
      const result = processor.processOrder(150, 'standard');
      expect(result.shipping).toBe(10);
      expect(result.total).toBe(145);
    });
  });
});

// GREEN: Implement order processor
interface OrderResult {
  subtotal: number;
  discount: number;
  shipping: number;
  total: number;
}

class OrderProcessor {
  calculateDiscount(amount: number): number {
    if (amount >= 1000) return amount * 0.3;
    if (amount >= 500) return amount * 0.2;
    if (amount >= 100) return amount * 0.1;
    return 0;
  }

  processOrder(amount: number, tier: string): OrderResult {
    const discount = this.calculateDiscount(amount);
    const shipping = tier === 'premium' ? 0 : 10;
    const total = amount - discount + shipping;

    return {
      subtotal: amount,
      discount,
      shipping,
      total,
    };
  }
}
