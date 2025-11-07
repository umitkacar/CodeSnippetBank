/**
 * AES Encryption (TypeScript)
 * Production-ready AES encryption with multiple modes
 */
import * as crypto from 'crypto';

export class AESEncryption {
  private keySize: number;

  constructor(keySize: number = 256) {
    if (![128, 192, 256].includes(keySize)) {
      throw new Error('Key size must be 128, 192, or 256 bits');
    }
    this.keySize = keySize;
  }

  generateKey(): Buffer {
    return crypto.randomBytes(this.keySize / 8);
  }

  encryptGCM(plaintext: Buffer, key: Buffer, aad: Buffer = Buffer.alloc(0)): {
    iv: Buffer;
    ciphertext: Buffer;
    authTag: Buffer;
  } {
    const iv = crypto.randomBytes(12);
    const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);

    if (aad.length > 0) {
      cipher.setAAD(aad);
    }

    const ciphertext = Buffer.concat([cipher.update(plaintext), cipher.final()]);
    const authTag = cipher.getAuthTag();

    return { iv, ciphertext, authTag };
  }

  decryptGCM(
    ciphertext: Buffer,
    key: Buffer,
    iv: Buffer,
    authTag: Buffer,
    aad: Buffer = Buffer.alloc(0)
  ): Buffer {
    const decipher = crypto.createDecipheriv('aes-256-gcm', key, iv);
    decipher.setAuthTag(authTag);

    if (aad.length > 0) {
      decipher.setAAD(aad);
    }

    return Buffer.concat([decipher.update(ciphertext), decipher.final()]);
  }

  encryptCBC(plaintext: Buffer, key: Buffer): {
    iv: Buffer;
    ciphertext: Buffer;
  } {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);
    const ciphertext = Buffer.concat([cipher.update(plaintext), cipher.final()]);
    return { iv, ciphertext };
  }

  decryptCBC(ciphertext: Buffer, key: Buffer, iv: Buffer): Buffer {
    const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);
    return Buffer.concat([decipher.update(ciphertext), decipher.final()]);
  }
}

// Example
if (require.main === module) {
  const aes = new AESEncryption(256);
  const key = aes.generateKey();
  const plaintext = Buffer.from('Secret message');

  const encrypted = aes.encryptGCM(plaintext, key);
  console.log('✓ Encrypted with AES-GCM');

  const decrypted = aes.decryptGCM(encrypted.ciphertext, key, encrypted.iv, encrypted.authTag);
  console.log('✓ Decrypted:', decrypted.toString());
}
