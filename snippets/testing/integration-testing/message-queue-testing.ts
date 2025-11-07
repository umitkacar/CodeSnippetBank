// Message Queue Integration Testing
// Testing queue operations and message processing

describe('Message Queue Integration', () => {
  interface Message {
    id: string;
    data: any;
    timestamp: number;
  }

  class MockMessageQueue {
    private queue: Message[] = [];

    async publish(data: any): Promise<string> {
      const message: Message = {
        id: Math.random().toString(36),
        data,
        timestamp: Date.now(),
      };
      this.queue.push(message);
      return message.id;
    }

    async consume(handler: (message: Message) => Promise<void>): Promise<void> {
      while (this.queue.length > 0) {
        const message = this.queue.shift();
        if (message) {
          await handler(message);
        }
      }
    }

    async size(): Promise<number> {
      return this.queue.length;
    }

    async clear(): Promise<void> {
      this.queue = [];
    }
  }

  let queue: MockMessageQueue;

  beforeEach(() => {
    queue = new MockMessageQueue();
  });

  afterEach(async () => {
    await queue.clear();
  });

  test('publishes message', async () => {
    const messageId = await queue.publish({ text: 'Hello' });
    expect(messageId).toBeDefined();
    expect(await queue.size()).toBe(1);
  });

  test('consumes messages', async () => {
    await queue.publish({ text: 'Message 1' });
    await queue.publish({ text: 'Message 2' });

    const received: Message[] = [];
    await queue.consume(async (msg) => {
      received.push(msg);
    });

    expect(received).toHaveLength(2);
    expect(await queue.size()).toBe(0);
  });
});
