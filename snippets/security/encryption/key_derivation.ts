/**
 * Key Derivation Functions (TypeScript)
 */
import * as crypto from 'crypto';

export class KeyDerivation {
  static pbkdf2(password: Buffer, salt?: Buffer, iterations: number = 100000): {
    key: Buffer;
    salt: Buffer;
  } {
    const saltBuf = salt || crypto.randomBytes(16);
    const key = crypto.pbkdf2Sync(password, saltBuf, iterations, 32, 'sha256');
    return { key, salt: saltBuf };
  }

  static scrypt(password: Buffer, salt?: Buffer): {
    key: Buffer;
    salt: Buffer;
  } {
    const saltBuf = salt || crypto.randomBytes(16);
    const key = crypto.scryptSync(password, saltBuf, 32);
    return { key, salt: saltBuf };
  }

  static hkdf(keyMaterial: Buffer, info: Buffer = Buffer.alloc(0), length: number = 32): Buffer {
    return crypto.hkdfSync('sha256', keyMaterial, Buffer.alloc(0), info, length);
  }
}
