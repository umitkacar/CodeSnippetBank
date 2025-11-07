/**
 * CSRF Protection (TypeScript)
 */
import * as crypto from 'crypto';

export class CSRFProtection {
  private secretKey: Buffer;

  constructor(secretKey: string) {
    this.secretKey = Buffer.from(secretKey);
  }

  generateToken(sessionId: string): string {
    const randomPart = crypto.randomBytes(32).toString('base64url');
    const signature = crypto
      .createHmac('sha256', this.secretKey)
      .update(`${sessionId}:${randomPart}`)
      .digest('hex');
    return `${randomPart}.${signature}`;
  }

  verifyToken(token: string, sessionId: string): boolean {
    try {
      const [randomPart, signature] = token.split('.');
      const expectedSig = crypto
        .createHmac('sha256', this.secretKey)
        .update(`${sessionId}:${randomPart}`)
        .digest('hex');
      return crypto.timingSafeEqual(
        Buffer.from(signature),
        Buffer.from(expectedSig)
      );
    } catch {
      return false;
    }
  }
}
