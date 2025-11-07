import { MMKV } from 'react-native-mmkv';

// Create storage instance
export const storage = new MMKV({
  id: 'app-storage',
  encryptionKey: 'your-encryption-key',
});

export class MMKVStorage {
  // String operations
  static set(key: string, value: string): void {
    storage.set(key, value);
  }

  static getString(key: string): string | undefined {
    return storage.getString(key);
  }

  // Number operations
  static setNumber(key: string, value: number): void {
    storage.set(key, value);
  }

  static getNumber(key: string): number | undefined {
    return storage.getNumber(key);
  }

  // Boolean operations
  static setBoolean(key: string, value: boolean): void {
    storage.set(key, value);
  }

  static getBoolean(key: string): boolean | undefined {
    return storage.getBoolean(key);
  }

  // Object operations
  static setObject<T>(key: string, value: T): void {
    storage.set(key, JSON.stringify(value));
  }

  static getObject<T>(key: string): T | undefined {
    const value = storage.getString(key);
    return value ? JSON.parse(value) : undefined;
  }

  // Delete
  static delete(key: string): void {
    storage.delete(key);
  }

  // Check if key exists
  static contains(key: string): boolean {
    return storage.contains(key);
  }

  // Get all keys
  static getAllKeys(): string[] {
    return storage.getAllKeys();
  }

  // Clear all
  static clearAll(): void {
    storage.clearAll();
  }

  // Add listener
  static addListener(callback: (key: string) => void): () => void {
    return storage.addOnValueChangedListener(callback);
  }
}

// Zustand MMKV persistence
export const mmkvStorage = {
  setItem: (name: string, value: string) => {
    storage.set(name, value);
  },
  getItem: (name: string) => {
    const value = storage.getString(name);
    return value ?? null;
  },
  removeItem: (name: string) => {
    storage.delete(name);
  },
};
