// State Machine Testing
// Testing state transitions and state management

describe('State Machine Testing', () => {
  // Basic state machine
  describe('Basic State Machine', () => {
    type State = 'idle' | 'loading' | 'success' | 'error';

    class DataFetcher {
      private state: State = 'idle';

      getState(): State {
        return this.state;
      }

      startFetch(): void {
        if (this.state !== 'idle') {
          throw new Error('Cannot start fetch from non-idle state');
        }
        this.state = 'loading';
      }

      onSuccess(): void {
        if (this.state !== 'loading') {
          throw new Error('Must be loading to succeed');
        }
        this.state = 'success';
      }

      onError(): void {
        if (this.state !== 'loading') {
          throw new Error('Must be loading to error');
        }
        this.state = 'error';
      }

      reset(): void {
        this.state = 'idle';
      }
    }

    test('starts in idle state', () => {
      const fetcher = new DataFetcher();
      expect(fetcher.getState()).toBe('idle');
    });

    test('transitions to loading', () => {
      const fetcher = new DataFetcher();
      fetcher.startFetch();
      expect(fetcher.getState()).toBe('loading');
    });

    test('transitions to success', () => {
      const fetcher = new DataFetcher();
      fetcher.startFetch();
      fetcher.onSuccess();
      expect(fetcher.getState()).toBe('success');
    });

    test('transitions to error', () => {
      const fetcher = new DataFetcher();
      fetcher.startFetch();
      fetcher.onError();
      expect(fetcher.getState()).toBe('error');
    });

    test('resets to idle', () => {
      const fetcher = new DataFetcher();
      fetcher.startFetch();
      fetcher.onSuccess();
      fetcher.reset();
      expect(fetcher.getState()).toBe('idle');
    });

    test('throws on invalid transitions', () => {
      const fetcher = new DataFetcher();
      expect(() => fetcher.onSuccess()).toThrow();
      expect(() => fetcher.onError()).toThrow();
    });
  });

  // Order state machine
  describe('Order State Machine', () => {
    type OrderState = 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';

    class Order {
      private state: OrderState = 'pending';

      getState(): OrderState {
        return this.state;
      }

      process(): void {
        if (this.state !== 'pending') {
          throw new Error('Can only process pending orders');
        }
        this.state = 'processing';
      }

      ship(): void {
        if (this.state !== 'processing') {
          throw new Error('Can only ship processing orders');
        }
        this.state = 'shipped';
      }

      deliver(): void {
        if (this.state !== 'shipped') {
          throw new Error('Can only deliver shipped orders');
        }
        this.state = 'delivered';
      }

      cancel(): void {
        if (this.state === 'delivered') {
          throw new Error('Cannot cancel delivered orders');
        }
        this.state = 'cancelled';
      }

      canCancel(): boolean {
        return this.state !== 'delivered';
      }
    }

    test('complete order flow', () => {
      const order = new Order();
      expect(order.getState()).toBe('pending');

      order.process();
      expect(order.getState()).toBe('processing');

      order.ship();
      expect(order.getState()).toBe('shipped');

      order.deliver();
      expect(order.getState()).toBe('delivered');
    });

    test('cancels at different stages', () => {
      const order1 = new Order();
      order1.cancel();
      expect(order1.getState()).toBe('cancelled');

      const order2 = new Order();
      order2.process();
      order2.cancel();
      expect(order2.getState()).toBe('cancelled');

      const order3 = new Order();
      order3.process();
      order3.ship();
      order3.cancel();
      expect(order3.getState()).toBe('cancelled');
    });

    test('cannot cancel delivered order', () => {
      const order = new Order();
      order.process();
      order.ship();
      order.deliver();

      expect(() => order.cancel()).toThrow('Cannot cancel delivered orders');
      expect(order.canCancel()).toBe(false);
    });
  });

  // Traffic light state machine
  describe('Traffic Light', () => {
    type LightState = 'red' | 'yellow' | 'green';

    class TrafficLight {
      private state: LightState = 'red';

      getState(): LightState {
        return this.state;
      }

      next(): void {
        switch (this.state) {
          case 'red':
            this.state = 'green';
            break;
          case 'green':
            this.state = 'yellow';
            break;
          case 'yellow':
            this.state = 'red';
            break;
        }
      }

      canGo(): boolean {
        return this.state === 'green';
      }

      shouldStop(): boolean {
        return this.state === 'red';
      }

      shouldPrepare(): boolean {
        return this.state === 'yellow';
      }
    }

    test('cycles through states', () => {
      const light = new TrafficLight();

      expect(light.getState()).toBe('red');
      light.next();
      expect(light.getState()).toBe('green');
      light.next();
      expect(light.getState()).toBe('yellow');
      light.next();
      expect(light.getState()).toBe('red');
    });

    test('checks permissions', () => {
      const light = new TrafficLight();

      expect(light.shouldStop()).toBe(true);
      expect(light.canGo()).toBe(false);

      light.next(); // green
      expect(light.canGo()).toBe(true);
      expect(light.shouldStop()).toBe(false);

      light.next(); // yellow
      expect(light.shouldPrepare()).toBe(true);
    });
  });

  // Document workflow
  describe('Document Workflow', () => {
    type DocumentState = 'draft' | 'review' | 'approved' | 'published' | 'archived';

    interface User {
      role: 'author' | 'reviewer' | 'admin';
    }

    class Document {
      private state: DocumentState = 'draft';

      getState(): DocumentState {
        return this.state;
      }

      submitForReview(user: User): void {
        if (user.role !== 'author' && user.role !== 'admin') {
          throw new Error('Only authors can submit');
        }
        if (this.state !== 'draft') {
          throw new Error('Can only submit drafts');
        }
        this.state = 'review';
      }

      approve(user: User): void {
        if (user.role !== 'reviewer' && user.role !== 'admin') {
          throw new Error('Only reviewers can approve');
        }
        if (this.state !== 'review') {
          throw new Error('Can only approve documents in review');
        }
        this.state = 'approved';
      }

      publish(user: User): void {
        if (user.role !== 'admin') {
          throw new Error('Only admins can publish');
        }
        if (this.state !== 'approved') {
          throw new Error('Can only publish approved documents');
        }
        this.state = 'published';
      }

      archive(user: User): void {
        if (user.role !== 'admin') {
          throw new Error('Only admins can archive');
        }
        if (this.state !== 'published') {
          throw new Error('Can only archive published documents');
        }
        this.state = 'archived';
      }
    }

    test('complete workflow with proper roles', () => {
      const doc = new Document();
      const author: User = { role: 'author' };
      const reviewer: User = { role: 'reviewer' };
      const admin: User = { role: 'admin' };

      doc.submitForReview(author);
      expect(doc.getState()).toBe('review');

      doc.approve(reviewer);
      expect(doc.getState()).toBe('approved');

      doc.publish(admin);
      expect(doc.getState()).toBe('published');

      doc.archive(admin);
      expect(doc.getState()).toBe('archived');
    });

    test('enforces role permissions', () => {
      const doc = new Document();
      const author: User = { role: 'author' };

      doc.submitForReview(author);

      expect(() => doc.approve(author)).toThrow('Only reviewers can approve');
      expect(() => doc.publish(author)).toThrow('Only admins can publish');
    });
  });

  // Connection state machine
  describe('Connection State Machine', () => {
    type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'reconnecting';

    class Connection {
      private state: ConnectionState = 'disconnected';
      private retryCount = 0;
      private maxRetries = 3;

      getState(): ConnectionState {
        return this.state;
      }

      getRetryCount(): number {
        return this.retryCount;
      }

      connect(): void {
        if (this.state === 'connected') {
          throw new Error('Already connected');
        }
        this.state = 'connecting';
        this.retryCount = 0;
      }

      onConnected(): void {
        if (this.state !== 'connecting' && this.state !== 'reconnecting') {
          throw new Error('Invalid state for connection success');
        }
        this.state = 'connected';
        this.retryCount = 0;
      }

      onDisconnected(): void {
        if (this.state !== 'connected') {
          return;
        }
        this.state = 'disconnected';
      }

      onConnectionFailed(): void {
        if (this.state !== 'connecting' && this.state !== 'reconnecting') {
          return;
        }

        this.retryCount++;
        if (this.retryCount < this.maxRetries) {
          this.state = 'reconnecting';
        } else {
          this.state = 'disconnected';
        }
      }
    }

    test('successful connection', () => {
      const conn = new Connection();

      conn.connect();
      expect(conn.getState()).toBe('connecting');

      conn.onConnected();
      expect(conn.getState()).toBe('connected');
    });

    test('disconnection', () => {
      const conn = new Connection();
      conn.connect();
      conn.onConnected();

      conn.onDisconnected();
      expect(conn.getState()).toBe('disconnected');
    });

    test('retry logic', () => {
      const conn = new Connection();
      conn.connect();

      conn.onConnectionFailed();
      expect(conn.getState()).toBe('reconnecting');
      expect(conn.getRetryCount()).toBe(1);

      conn.onConnectionFailed();
      expect(conn.getState()).toBe('reconnecting');
      expect(conn.getRetryCount()).toBe(2);

      conn.onConnectionFailed();
      expect(conn.getState()).toBe('disconnected');
      expect(conn.getRetryCount()).toBe(3);
    });

    test('successful reconnection', () => {
      const conn = new Connection();
      conn.connect();
      conn.onConnectionFailed();

      expect(conn.getState()).toBe('reconnecting');

      conn.onConnected();
      expect(conn.getState()).toBe('connected');
      expect(conn.getRetryCount()).toBe(0);
    });
  });
});
