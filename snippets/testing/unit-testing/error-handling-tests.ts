// Error Handling Testing Patterns
// Comprehensive error testing examples

describe('Error Handling Tests', () => {
  // Basic error throwing
  describe('Synchronous Errors', () => {
    test('throws error', () => {
      function throwError(): never {
        throw new Error('Something went wrong');
      }

      expect(() => throwError()).toThrow();
      expect(() => throwError()).toThrow(Error);
      expect(() => throwError()).toThrow('Something went wrong');
    });

    test('throws specific error type', () => {
      function throwTypeError(): never {
        throw new TypeError('Invalid type');
      }

      expect(() => throwTypeError()).toThrow(TypeError);
      expect(() => throwTypeError()).toThrow('Invalid type');
    });

    test('throws with regex match', () => {
      function throwError(): never {
        throw new Error('Error code: 404');
      }

      expect(() => throwError()).toThrow(/404/);
      expect(() => throwError()).toThrow(/Error code:/);
    });
  });

  // Async error handling
  describe('Asynchronous Errors', () => {
    test('rejects promise', async () => {
      async function rejectPromise(): Promise<never> {
        throw new Error('Async error');
      }

      await expect(rejectPromise()).rejects.toThrow('Async error');
    });

    test('rejects with specific error', async () => {
      async function rejectWithType(): Promise<never> {
        throw new TypeError('Type error');
      }

      await expect(rejectWithType()).rejects.toThrow(TypeError);
    });

    test('handles promise rejection', async () => {
      const promise = Promise.reject(new Error('Rejected'));
      await expect(promise).rejects.toThrow('Rejected');
    });
  });

  // Custom errors
  describe('Custom Errors', () => {
    class ValidationError extends Error {
      constructor(message: string, public field: string) {
        super(message);
        this.name = 'ValidationError';
      }
    }

    class AuthenticationError extends Error {
      constructor(message: string, public code: number) {
        super(message);
        this.name = 'AuthenticationError';
      }
    }

    test('throws custom validation error', () => {
      function validate(input: string): void {
        if (!input) {
          throw new ValidationError('Field is required', 'username');
        }
      }

      expect(() => validate('')).toThrow(ValidationError);
      expect(() => validate('')).toThrow('Field is required');
    });

    test('throws custom authentication error', () => {
      function authenticate(token: string): void {
        if (!token) {
          throw new AuthenticationError('Unauthorized', 401);
        }
      }

      expect(() => authenticate('')).toThrow(AuthenticationError);
      expect(() => authenticate('')).toThrow('Unauthorized');
    });

    test('catches and inspects custom error', () => {
      function validate(): void {
        throw new ValidationError('Invalid email', 'email');
      }

      try {
        validate();
      } catch (error) {
        expect(error).toBeInstanceOf(ValidationError);
        expect((error as ValidationError).field).toBe('email');
      }
    });
  });

  // Error boundaries
  describe('Error Boundaries', () => {
    class ErrorBoundary {
      private errorHandler: ((error: Error) => void) | null = null;

      setErrorHandler(handler: (error: Error) => void): void {
        this.errorHandler = handler;
      }

      execute(fn: () => void): void {
        try {
          fn();
        } catch (error) {
          if (this.errorHandler && error instanceof Error) {
            this.errorHandler(error);
          } else {
            throw error;
          }
        }
      }
    }

    test('catches errors in boundary', () => {
      const boundary = new ErrorBoundary();
      const errorHandler = jest.fn();
      boundary.setErrorHandler(errorHandler);

      boundary.execute(() => {
        throw new Error('Caught error');
      });

      expect(errorHandler).toHaveBeenCalledWith(expect.any(Error));
      expect(errorHandler).toHaveBeenCalledWith(
        expect.objectContaining({ message: 'Caught error' })
      );
    });

    test('rethrows if no handler', () => {
      const boundary = new ErrorBoundary();

      expect(() => {
        boundary.execute(() => {
          throw new Error('Unhandled');
        });
      }).toThrow('Unhandled');
    });
  });

  // Error recovery
  describe('Error Recovery', () => {
    class RetryableOperation {
      private attempts = 0;

      async execute(
        fn: () => Promise<any>,
        maxRetries = 3
      ): Promise<any> {
        this.attempts = 0;
        let lastError: Error | null = null;

        while (this.attempts < maxRetries) {
          try {
            this.attempts++;
            return await fn();
          } catch (error) {
            lastError = error as Error;
            if (this.attempts >= maxRetries) {
              throw lastError;
            }
          }
        }

        throw lastError;
      }

      getAttempts(): number {
        return this.attempts;
      }
    }

    test('retries on failure', async () => {
      const operation = new RetryableOperation();
      let callCount = 0;

      const fn = jest.fn(async () => {
        callCount++;
        if (callCount < 3) {
          throw new Error('Failed');
        }
        return 'success';
      });

      const result = await operation.execute(fn);

      expect(result).toBe('success');
      expect(operation.getAttempts()).toBe(3);
      expect(fn).toHaveBeenCalledTimes(3);
    });

    test('throws after max retries', async () => {
      const operation = new RetryableOperation();

      const fn = jest.fn(async () => {
        throw new Error('Always fails');
      });

      await expect(operation.execute(fn)).rejects.toThrow('Always fails');
      expect(operation.getAttempts()).toBe(3);
    });
  });

  // Error aggregation
  describe('Error Aggregation', () => {
    class AggregateError extends Error {
      constructor(public errors: Error[]) {
        super(`Multiple errors occurred: ${errors.length}`);
        this.name = 'AggregateError';
      }
    }

    class BatchProcessor {
      async processBatch(items: any[]): Promise<void> {
        const errors: Error[] = [];

        for (const item of items) {
          try {
            await this.processItem(item);
          } catch (error) {
            errors.push(error as Error);
          }
        }

        if (errors.length > 0) {
          throw new AggregateError(errors);
        }
      }

      private async processItem(item: any): Promise<void> {
        if (item.shouldFail) {
          throw new Error(`Failed to process ${item.id}`);
        }
      }
    }

    test('aggregates multiple errors', async () => {
      const processor = new BatchProcessor();
      const items = [
        { id: 1, shouldFail: true },
        { id: 2, shouldFail: false },
        { id: 3, shouldFail: true },
      ];

      try {
        await processor.processBatch(items);
      } catch (error) {
        expect(error).toBeInstanceOf(AggregateError);
        expect((error as AggregateError).errors).toHaveLength(2);
      }
    });
  });

  // Error logging
  describe('Error Logging', () => {
    interface ErrorLogger {
      log(error: Error): void;
    }

    class ErrorHandler {
      constructor(private logger: ErrorLogger) {}

      handle(error: Error): void {
        this.logger.log(error);
      }

      async handleAsync(fn: () => Promise<void>): Promise<void> {
        try {
          await fn();
        } catch (error) {
          this.logger.log(error as Error);
          throw error;
        }
      }
    }

    test('logs errors', () => {
      const logger = { log: jest.fn() };
      const handler = new ErrorHandler(logger);
      const error = new Error('Test error');

      handler.handle(error);

      expect(logger.log).toHaveBeenCalledWith(error);
    });

    test('logs and rethrows async errors', async () => {
      const logger = { log: jest.fn() };
      const handler = new ErrorHandler(logger);

      await expect(
        handler.handleAsync(async () => {
          throw new Error('Async error');
        })
      ).rejects.toThrow('Async error');

      expect(logger.log).toHaveBeenCalled();
    });
  });

  // Error transformation
  describe('Error Transformation', () => {
    class ApiError extends Error {
      constructor(
        message: string,
        public statusCode: number,
        public originalError?: Error
      ) {
        super(message);
        this.name = 'ApiError';
      }
    }

    function transformError(error: Error): ApiError {
      if (error.message.includes('timeout')) {
        return new ApiError('Request timeout', 504, error);
      }
      if (error.message.includes('not found')) {
        return new ApiError('Resource not found', 404, error);
      }
      return new ApiError('Internal server error', 500, error);
    }

    test('transforms timeout error', () => {
      const original = new Error('Request timeout');
      const transformed = transformError(original);

      expect(transformed).toBeInstanceOf(ApiError);
      expect(transformed.statusCode).toBe(504);
      expect(transformed.originalError).toBe(original);
    });

    test('transforms not found error', () => {
      const original = new Error('Resource not found');
      const transformed = transformError(original);

      expect(transformed.statusCode).toBe(404);
    });

    test('transforms generic error', () => {
      const original = new Error('Something went wrong');
      const transformed = transformError(original);

      expect(transformed.statusCode).toBe(500);
    });
  });

  // Error context
  describe('Error Context', () => {
    class ContextualError extends Error {
      constructor(
        message: string,
        public context: Record<string, any>
      ) {
        super(message);
        this.name = 'ContextualError';
      }
    }

    function processWithContext(data: any): void {
      try {
        if (!data.id) {
          throw new ContextualError('Missing ID', { data, operation: 'process' });
        }
      } catch (error) {
        if (error instanceof ContextualError) {
          throw error;
        }
        throw new ContextualError('Processing failed', {
          originalError: error,
          data,
        });
      }
    }

    test('includes context in error', () => {
      const data = { name: 'Test' };

      try {
        processWithContext(data);
      } catch (error) {
        expect(error).toBeInstanceOf(ContextualError);
        expect((error as ContextualError).context.data).toEqual(data);
        expect((error as ContextualError).context.operation).toBe('process');
      }
    });
  });
});
