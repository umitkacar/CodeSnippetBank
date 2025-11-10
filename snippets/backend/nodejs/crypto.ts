/**
 * Crypto Operations in Node.js
 */
import crypto from 'crypto';

// Generate random bytes
export function generateRandomBytes(size: number = 32): string {
  try {
    return crypto.randomBytes(size).toString('hex');
  } catch (error) {
    throw new Error(`Failed to generate random bytes: ${error}`);
  }
}

// Hash data with SHA-256
export function hashSHA256(data: string): string {
  try {
    return crypto.createHash('sha256').update(data).digest('hex');
  } catch (error) {
    throw new Error(`Failed to hash data: ${error}`);
  }
}

// Hash data with SHA-512
export function hashSHA512(data: string): string {
  try {
    return crypto.createHash('sha512').update(data).digest('hex');
  } catch (error) {
    throw new Error(`Failed to hash data: ${error}`);
  }
}

// HMAC
export function createHMAC(data: string, secret: string): string {
  try {
    return crypto.createHmac('sha256', secret).update(data).digest('hex');
  } catch (error) {
    throw new Error(`Failed to create HMAC: ${error}`);
  }
}

// Verify HMAC
export function verifyHMAC(data: string, secret: string, signature: string): boolean {
  try {
    const expectedSignature = createHMAC(data, secret);
    return crypto.timingSafeEqual(
      Buffer.from(signature),
      Buffer.from(expectedSignature)
    );
  } catch (error) {
    return false;
  }
}

// Encrypt data (AES-256-GCM)
export function encrypt(text: string, key: string): {
  encrypted: string;
  iv: string;
  tag: string;
} {
  try {
    const iv = crypto.randomBytes(16);
    const keyBuffer = crypto.scryptSync(key, 'salt', 32);
    const cipher = crypto.createCipheriv('aes-256-gcm', keyBuffer, iv);

    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    const tag = cipher.getAuthTag();

    return {
      encrypted,
      iv: iv.toString('hex'),
      tag: tag.toString('hex'),
    };
  } catch (error) {
    throw new Error(`Encryption failed: ${error}`);
  }
}

// Decrypt data (AES-256-GCM)
export function decrypt(
  encrypted: string,
  key: string,
  iv: string,
  tag: string
): string {
  try {
    const keyBuffer = crypto.scryptSync(key, 'salt', 32);
    const decipher = crypto.createDecipheriv(
      'aes-256-gcm',
      keyBuffer,
      Buffer.from(iv, 'hex')
    );
    decipher.setAuthTag(Buffer.from(tag, 'hex'));

    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');

    return decrypted;
  } catch (error) {
    throw new Error(`Decryption failed: ${error}`);
  }
}

// Generate UUID v4
export function generateUUID(): string {
  return crypto.randomUUID();
}

// Password-based key derivation
export function deriveKey(
  password: string,
  salt: string = 'default-salt',
  keyLength: number = 32
): string {
  try {
    return crypto.scryptSync(password, salt, keyLength).toString('hex');
  } catch (error) {
    throw new Error(`Key derivation failed: ${error}`);
  }
}
