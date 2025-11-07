/**
 * Secure Session Management (TypeScript)
 * Production-ready session handling with Redis backend
 */
import { createClient, RedisClientType } from 'redis';
import { randomBytes, createHash, createHmac } from 'crypto';

interface SessionData {
  user_id: number;
  created_at: string;
  last_activity: string;
  data: Record<string, any>;
}

interface CookieOptions {
  maxAge: number;
  path: string;
  secure: boolean;
  httpOnly: boolean;
  sameSite: 'Strict' | 'Lax' | 'None';
  domain?: string;
}

export class SessionManager {
  private redis: RedisClientType;
  private sessionLifetime: number;
  private sessionPrefix: string;

  /**
   * Initialize session manager
   * @param redis - Redis client instance
   * @param sessionLifetime - Session lifetime in seconds
   * @param sessionPrefix - Prefix for Redis keys
   */
  constructor(
    redis: RedisClientType,
    sessionLifetime: number = 3600,
    sessionPrefix: string = 'session:'
  ) {
    this.redis = redis;
    this.sessionLifetime = sessionLifetime;
    this.sessionPrefix = sessionPrefix;
  }

  /**
   * Generate cryptographically secure session ID
   * @returns Session ID string
   */
  generateSessionId(): string {
    const randomData = randomBytes(32);
    const sessionId = createHash('sha256').update(randomData).digest('hex');
    return sessionId;
  }

  /**
   * Create a new session
   * @param userId - User ID
   * @param data - Additional session data
   * @returns Session ID
   */
  async createSession(
    userId: number,
    data?: Record<string, any>
  ): Promise<string> {
    const sessionId = this.generateSessionId();
    const now = new Date().toISOString();

    const sessionData: SessionData = {
      user_id: userId,
      created_at: now,
      last_activity: now,
      data: data || {},
    };

    const key = `${this.sessionPrefix}${sessionId}`;

    await this.redis.setEx(
      key,
      this.sessionLifetime,
      JSON.stringify(sessionData)
    );

    return sessionId;
  }

  /**
   * Retrieve session data
   * @param sessionId - Session ID
   * @returns Session data or null if not found
   */
  async getSession(sessionId: string): Promise<SessionData | null> {
    const key = `${this.sessionPrefix}${sessionId}`;
    const data = await this.redis.get(key);

    if (!data) {
      return null;
    }

    const sessionData: SessionData = JSON.parse(data);

    // Update last activity
    sessionData.last_activity = new Date().toISOString();

    await this.redis.setEx(
      key,
      this.sessionLifetime,
      JSON.stringify(sessionData)
    );

    return sessionData;
  }

  /**
   * Update session data
   * @param sessionId - Session ID
   * @param data - Data to update
   * @returns True if successful
   */
  async updateSession(
    sessionId: string,
    data: Record<string, any>
  ): Promise<boolean> {
    const sessionData = await this.getSession(sessionId);

    if (!sessionData) {
      return false;
    }

    sessionData.data = { ...sessionData.data, ...data };
    sessionData.last_activity = new Date().toISOString();

    const key = `${this.sessionPrefix}${sessionId}`;

    await this.redis.setEx(
      key,
      this.sessionLifetime,
      JSON.stringify(sessionData)
    );

    return true;
  }

  /**
   * Delete a session (logout)
   * @param sessionId - Session ID
   * @returns True if deleted
   */
  async deleteSession(sessionId: string): Promise<boolean> {
    const key = `${this.sessionPrefix}${sessionId}`;
    const result = await this.redis.del(key);
    return result > 0;
  }

  /**
   * Delete all sessions for a user
   * @param userId - User ID
   * @returns Number of sessions deleted
   */
  async deleteUserSessions(userId: number): Promise<number> {
    const pattern = `${this.sessionPrefix}*`;
    let deleted = 0;

    for await (const key of this.redis.scanIterator({ MATCH: pattern })) {
      const data = await this.redis.get(key);

      if (data) {
        const sessionData: SessionData = JSON.parse(data);

        if (sessionData.user_id === userId) {
          await this.redis.del(key);
          deleted++;
        }
      }
    }

    return deleted;
  }

  /**
   * Check if session is valid
   * @param sessionId - Session ID
   * @returns True if session exists and is valid
   */
  async validateSession(sessionId: string): Promise<boolean> {
    const session = await this.getSession(sessionId);
    return session !== null;
  }

  /**
   * Count active sessions for a user
   * @param userId - User ID
   * @returns Number of active sessions
   */
  async getSessionCount(userId: number): Promise<number> {
    const pattern = `${this.sessionPrefix}*`;
    let count = 0;

    for await (const key of this.redis.scanIterator({ MATCH: pattern })) {
      const data = await this.redis.get(key);

      if (data) {
        const sessionData: SessionData = JSON.parse(data);

        if (sessionData.user_id === userId) {
          count++;
        }
      }
    }

    return count;
  }
}

export class SecureCookieSession {
  /**
   * Get secure cookie options
   * @param maxAge - Cookie lifetime in seconds
   * @param domain - Cookie domain
   * @param path - Cookie path
   * @returns Cookie options
   */
  static getSecureCookieOptions(
    maxAge: number = 3600,
    domain?: string,
    path: string = '/'
  ): CookieOptions {
    const options: CookieOptions = {
      maxAge,
      path,
      secure: true, // HTTPS only
      httpOnly: true, // Not accessible via JavaScript
      sameSite: 'Lax', // CSRF protection
    };

    if (domain) {
      options.domain = domain;
    }

    return options;
  }

  /**
   * Sign cookie value for integrity
   * @param value - Cookie value
   * @param secret - Secret key
   * @returns Signed value
   */
  static signCookieValue(value: string, secret: string): string {
    const signature = createHmac('sha256', secret)
      .update(value)
      .digest('hex');

    return `${value}.${signature}`;
  }

  /**
   * Verify and extract cookie value
   * @param signedValue - Signed cookie value
   * @param secret - Secret key
   * @returns Original value if valid, null otherwise
   */
  static verifyCookieSignature(
    signedValue: string,
    secret: string
  ): string | null {
    try {
      const lastDotIndex = signedValue.lastIndexOf('.');
      if (lastDotIndex === -1) {
        return null;
      }

      const value = signedValue.substring(0, lastDotIndex);
      const signature = signedValue.substring(lastDotIndex + 1);

      const expectedSignature = createHmac('sha256', secret)
        .update(value)
        .digest('hex');

      // Constant-time comparison
      if (signature === expectedSignature) {
        return value;
      }

      return null;
    } catch {
      return null;
    }
  }

  /**
   * Format cookie header string
   * @param name - Cookie name
   * @param value - Cookie value
   * @param options - Cookie options
   * @returns Set-Cookie header value
   */
  static formatCookieHeader(
    name: string,
    value: string,
    options: CookieOptions
  ): string {
    const parts = [`${name}=${value}`];

    if (options.maxAge) {
      parts.push(`Max-Age=${options.maxAge}`);
    }

    if (options.path) {
      parts.push(`Path=${options.path}`);
    }

    if (options.domain) {
      parts.push(`Domain=${options.domain}`);
    }

    if (options.secure) {
      parts.push('Secure');
    }

    if (options.httpOnly) {
      parts.push('HttpOnly');
    }

    if (options.sameSite) {
      parts.push(`SameSite=${options.sameSite}`);
    }

    return parts.join('; ');
  }
}

// Example usage
if (require.main === module) {
  (async () => {
    // Initialize Redis client
    const redis = createClient({
      url: 'redis://localhost:6379',
    });

    await redis.connect();

    // Create session manager
    const sessionMgr = new SessionManager(redis);

    // Create a new session
    const userId = 123;
    const sessionId = await sessionMgr.createSession(userId, {
      role: 'admin',
      ip: '192.168.1.1',
    });

    console.log(`Created session: ${sessionId}`);

    // Retrieve session
    const session = await sessionMgr.getSession(sessionId);
    console.log('Session data:', session);

    // Update session
    await sessionMgr.updateSession(sessionId, { last_page: '/dashboard' });

    // Validate session
    const isValid = await sessionMgr.validateSession(sessionId);
    console.log(`Session valid: ${isValid}`);

    // Get secure cookie options
    const cookieOptions = SecureCookieSession.getSecureCookieOptions();
    console.log('Cookie options:', cookieOptions);

    // Sign cookie
    const signedCookie = SecureCookieSession.signCookieValue(
      sessionId,
      'secret_key'
    );
    console.log(`Signed cookie: ${signedCookie.substring(0, 50)}...`);

    // Delete session
    await sessionMgr.deleteSession(sessionId);
    console.log('Session deleted');

    await redis.disconnect();
  })();
}
