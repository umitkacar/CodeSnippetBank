/**
 * EventEmitter Pattern in Node.js
 */
import { EventEmitter } from 'events';

export class CustomEventEmitter extends EventEmitter {
  constructor() {
    super();
    this.setMaxListeners(20);
  }

  // Type-safe event emission
  emitTyped<T>(event: string, data: T): boolean {
    return this.emit(event, data);
  }
}

// Example: User events
export interface UserEvents {
  created: { id: string; email: string };
  updated: { id: string; changes: Record<string, any> };
  deleted: { id: string };
}

export class UserEventEmitter extends EventEmitter {
  onUserCreated(callback: (data: UserEvents['created']) => void): this {
    return this.on('created', callback);
  }

  onUserUpdated(callback: (data: UserEvents['updated']) => void): this {
    return this.on('updated', callback);
  }

  onUserDeleted(callback: (data: UserEvents['deleted']) => void): this {
    return this.on('deleted', callback);
  }

  emitUserCreated(data: UserEvents['created']): boolean {
    return this.emit('created', data);
  }

  emitUserUpdated(data: UserEvents['updated']): boolean {
    return this.emit('updated', data);
  }

  emitUserDeleted(data: UserEvents['deleted']): boolean {
    return this.emit('deleted', data);
  }
}

// Example usage
export function setupUserEvents(): UserEventEmitter {
  const userEvents = new UserEventEmitter();

  userEvents.onUserCreated((data) => {
    console.log('User created:', data);
  });

  userEvents.onUserUpdated((data) => {
    console.log('User updated:', data);
  });

  userEvents.onUserDeleted((data) => {
    console.log('User deleted:', data);
  });

  return userEvents;
}

// Error handling
export class ErrorAwareEmitter extends EventEmitter {
  constructor() {
    super();
    this.on('error', (error) => {
      console.error('EventEmitter error:', error);
    });
  }

  safeEmit(event: string, ...args: any[]): boolean {
    try {
      return this.emit(event, ...args);
    } catch (error) {
      this.emit('error', error);
      return false;
    }
  }
}
