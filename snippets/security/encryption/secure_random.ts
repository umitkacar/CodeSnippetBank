/**
 * Secure Random Generation (TypeScript)
 */
import * as crypto from 'crypto';

export class SecureRandom {
  static generateToken(bytes: number = 32): string {
    return crypto.randomBytes(bytes).toString('base64url');
  }

  static generateHex(bytes: number = 32): string {
    return crypto.randomBytes(bytes).toString('hex');
  }

  static generateBytes(bytes: number = 32): Buffer {
    return crypto.randomBytes(bytes);
  }

  static generatePassword(length: number = 16, useSpecial: boolean = true): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const special = '!@#$%^&*()_+-=[]{}|;:,.<>?';
    const alphabet = useSpecial ? chars + special : chars;
    
    let password = '';
    for (let i = 0; i < length; i++) {
      const randomIndex = crypto.randomInt(0, alphabet.length);
      password += alphabet[randomIndex];
    }
    return password;
  }

  static generatePIN(length: number = 6): string {
    let pin = '';
    for (let i = 0; i < length; i++) {
      pin += crypto.randomInt(0, 10).toString();
    }
    return pin;
  }
}
