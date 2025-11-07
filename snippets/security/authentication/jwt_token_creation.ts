/**
 * JWT Token Creation and Validation (TypeScript)
 * Production-ready JWT implementation with security best practices
 */
import * as jwt from 'jsonwebtoken';
import { randomBytes } from 'crypto';

interface JWTPayload {
  [key: string]: any;
}

interface TokenOptions {
  expiresIn?: string | number;
}

export class JWTManager {
  private secretKey: string;
  private algorithm: jwt.Algorithm;

  constructor(secretKey?: string, algorithm: jwt.Algorithm = 'HS256') {
    this.secretKey = secretKey || randomBytes(32).toString('base64');
    this.algorithm = algorithm;
  }

  /**
   * Create a JWT access token
   * @param data - Payload data to encode
   * @param options - Token options (expiration, etc.)
   * @returns Encoded JWT token
   */
  createAccessToken(
    data: JWTPayload,
    options?: TokenOptions
  ): string {
    const payload = {
      ...data,
      iat: Math.floor(Date.now() / 1000),
      jti: randomBytes(16).toString('hex'), // JWT ID for revocation
    };

    const signOptions: jwt.SignOptions = {
      algorithm: this.algorithm,
      expiresIn: options?.expiresIn || '15m',
    };

    return jwt.sign(payload, this.secretKey, signOptions);
  }

  /**
   * Verify and decode JWT token
   * @param token - JWT token to verify
   * @returns Decoded payload or null if invalid
   */
  verifyToken(token: string): JWTPayload | null {
    try {
      const decoded = jwt.verify(token, this.secretKey, {
        algorithms: [this.algorithm],
      }) as JWTPayload;

      return decoded;
    } catch (error) {
      if (error instanceof jwt.TokenExpiredError) {
        console.error('Token has expired');
      } else if (error instanceof jwt.JsonWebTokenError) {
        console.error('Invalid token');
      }
      return null;
    }
  }

  /**
   * Create a long-lived refresh token
   * @param data - Payload data
   * @returns Refresh token
   */
  createRefreshToken(data: JWTPayload): string {
    const payload = {
      ...data,
      type: 'refresh',
    };

    return jwt.sign(payload, this.secretKey, {
      algorithm: this.algorithm,
      expiresIn: '30d',
    });
  }

  /**
   * Decode token without verification (for debugging)
   * @param token - JWT token
   * @returns Decoded payload
   */
  decodeToken(token: string): JWTPayload | null {
    return jwt.decode(token) as JWTPayload | null;
  }
}

// Example usage
if (require.main === module) {
  const jwtManager = new JWTManager();

  // Create access token
  const userData = { userId: 123, username: 'john_doe', role: 'admin' };
  const accessToken = jwtManager.createAccessToken(userData);
  console.log('Access Token:', accessToken);

  // Verify token
  const payload = jwtManager.verifyToken(accessToken);
  if (payload) {
    console.log('Verified Payload:', payload);
  }

  // Create refresh token
  const refreshToken = jwtManager.createRefreshToken({ userId: 123 });
  console.log('Refresh Token:', refreshToken);
}
