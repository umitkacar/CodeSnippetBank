import * as SecureStore from 'expo-secure-store';

export class SecureStorage {
  // Save secure data
  static async setItem(key: string, value: string): Promise<void> {
    try {
      await SecureStore.setItemAsync(key, value);
    } catch (error) {
      console.error('Error saving secure data:', error);
      throw error;
    }
  }

  // Get secure data
  static async getItem(key: string): Promise<string | null> {
    try {
      return await SecureStore.getItemAsync(key);
    } catch (error) {
      console.error('Error reading secure data:', error);
      return null;
    }
  }

  // Delete secure data
  static async removeItem(key: string): Promise<void> {
    try {
      await SecureStore.deleteItemAsync(key);
    } catch (error) {
      console.error('Error deleting secure data:', error);
      throw error;
    }
  }

  // Save object as secure data
  static async setObject<T>(key: string, value: T): Promise<void> {
    try {
      const jsonValue = JSON.stringify(value);
      await SecureStore.setItemAsync(key, jsonValue);
    } catch (error) {
      console.error('Error saving secure object:', error);
      throw error;
    }
  }

  // Get object from secure data
  static async getObject<T>(key: string): Promise<T | null> {
    try {
      const jsonValue = await SecureStore.getItemAsync(key);
      return jsonValue ? JSON.parse(jsonValue) : null;
    } catch (error) {
      console.error('Error reading secure object:', error);
      return null;
    }
  }
}

// Secure storage keys
export const SECURE_KEYS = {
  AUTH_TOKEN: 'secure_auth_token',
  REFRESH_TOKEN: 'secure_refresh_token',
  API_KEY: 'secure_api_key',
  USER_PIN: 'secure_user_pin',
  BIOMETRIC_KEY: 'secure_biometric_key',
  ENCRYPTION_KEY: 'secure_encryption_key',
} as const;

// Auth token management
export class AuthTokenManager {
  static async saveTokens(accessToken: string, refreshToken: string): Promise<void> {
    await Promise.all([
      SecureStorage.setItem(SECURE_KEYS.AUTH_TOKEN, accessToken),
      SecureStorage.setItem(SECURE_KEYS.REFRESH_TOKEN, refreshToken),
    ]);
  }

  static async getAccessToken(): Promise<string | null> {
    return SecureStorage.getItem(SECURE_KEYS.AUTH_TOKEN);
  }

  static async getRefreshToken(): Promise<string | null> {
    return SecureStorage.getItem(SECURE_KEYS.REFRESH_TOKEN);
  }

  static async clearTokens(): Promise<void> {
    await Promise.all([
      SecureStorage.removeItem(SECURE_KEYS.AUTH_TOKEN),
      SecureStorage.removeItem(SECURE_KEYS.REFRESH_TOKEN),
    ]);
  }

  static async hasValidToken(): Promise<boolean> {
    const token = await this.getAccessToken();
    return token !== null;
  }
}
