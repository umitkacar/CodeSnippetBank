/**
 * RSA Encryption (TypeScript)
 * Production-ready RSA asymmetric encryption
 */
import * as crypto from 'crypto';

export class RSAEncryption {
  static generateKeyPair(keySize: number = 2048): {
    privateKey: crypto.KeyObject;
    publicKey: crypto.KeyObject;
  } {
    return crypto.generateKeyPairSync('rsa', {
      modulusLength: keySize,
      publicKeyEncoding: { type: 'spki', format: 'pem' },
      privateKeyEncoding: { type: 'pkcs8', format: 'pem' },
    });
  }

  static encrypt(plaintext: Buffer, publicKey: crypto.KeyObject | string): Buffer {
    return crypto.publicEncrypt(
      {
        key: publicKey,
        padding: crypto.constants.RSA_PKCS1_OAEP_PADDING,
        oaepHash: 'sha256',
      },
      plaintext
    );
  }

  static decrypt(ciphertext: Buffer, privateKey: crypto.KeyObject | string): Buffer {
    return crypto.privateDecrypt(
      {
        key: privateKey,
        padding: crypto.constants.RSA_PKCS1_OAEP_PADDING,
        oaepHash: 'sha256',
      },
      ciphertext
    );
  }

  static sign(message: Buffer, privateKey: crypto.KeyObject | string): Buffer {
    return crypto.sign('sha256', message, privateKey);
  }

  static verify(
    message: Buffer,
    signature: Buffer,
    publicKey: crypto.KeyObject | string
  ): boolean {
    try {
      return crypto.verify('sha256', message, publicKey, signature);
    } catch {
      return false;
    }
  }
}

// Example
if (require.main === module) {
  const { privateKey, publicKey } = RSAEncryption.generateKeyPair(2048);
  const message = Buffer.from('Secret message');

  const encrypted = RSAEncryption.encrypt(message, publicKey);
  console.log('✓ Encrypted with RSA');

  const decrypted = RSAEncryption.decrypt(encrypted, privateKey);
  console.log('✓ Decrypted:', decrypted.toString());

  const signature = RSAEncryption.sign(message, privateKey);
  const isValid = RSAEncryption.verify(message, signature, publicKey);
  console.log('✓ Signature valid:', isValid);
}
