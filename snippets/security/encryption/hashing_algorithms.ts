/**
 * Hashing Algorithms (TypeScript)
 */
import * as crypto from 'crypto';

export class HashingAlgorithms {
  static sha256(data: Buffer): Buffer {
    return crypto.createHash('sha256').update(data).digest();
  }

  static sha512(data: Buffer): Buffer {
    return crypto.createHash('sha512').update(data).digest();
  }

  static blake2b(data: Buffer): Buffer {
    return crypto.createHash('blake2b512').update(data).digest();
  }

  static hmacSha256(data: Buffer, key: Buffer): Buffer {
    return crypto.createHmac('sha256', key).update(data).digest();
  }

  static verifyHmac(data: Buffer, key: Buffer, mac: Buffer): boolean {
    const expected = this.hmacSha256(data, key);
    return crypto.timingSafeEqual(expected, mac);
  }
}
