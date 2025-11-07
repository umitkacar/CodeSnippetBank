/**
 * API Key Management (TypeScript)
 * Production-ready API key generation, validation, and rate limiting
 */
import { randomBytes, createHmac, timingSafeEqual } from 'crypto';

interface APIKey {
  keyId: string;
  keyHash: string;
  name: string;
  userId: number;
  scopes: string[];
  createdAt: string;
  expiresAt?: string;
  lastUsed?: string;
  isActive: boolean;
}

interface RateLimitInfo {
  limit: number;
  remaining: number;
  reset: number;
  used: number;
}

export class APIKeyManager {
  private pepper: string;

  /**
   * Initialize API key manager
   * @param pepper - Secret pepper for additional security
   */
  constructor(pepper: string) {
    this.pepper = pepper;
  }

  /**
   * Generate a new API key
   * @returns Tuple of [keyId, apiKey]
   */
  generateAPIKey(): [string, string] {
    // Generate key ID (public)
    const keyId = `ak_${randomBytes(16).toString('base64url')}`;

    // Generate secret key (64 bytes = 512 bits)
    const apiKey = `sk_${randomBytes(48).toString('base64url')}`;

    return [keyId, apiKey];
  }

  /**
   * Hash API key for secure storage
   * @param apiKey - Plain API key
   * @returns Hashed key
   */
  hashAPIKey(apiKey: string): string {
    const hashed = createHmac('sha256', this.pepper)
      .update(apiKey)
      .digest('hex');

    return hashed;
  }

  /**
   * Create a new API key
   * @param userId - User ID
   * @param name - Key name/description
   * @param scopes - List of permissions
   * @param expiresInDays - Optional expiration in days
   * @returns Tuple of [plainApiKey, APIKey object]
   */
  createAPIKey(
    userId: number,
    name: string,
    scopes: string[],
    expiresInDays?: number
  ): [string, APIKey] {
    const [keyId, apiKey] = this.generateAPIKey();
    const keyHash = this.hashAPIKey(apiKey);

    const now = new Date();
    let expiresAt: string | undefined;

    if (expiresInDays) {
      const expiration = new Date(now);
      expiration.setDate(expiration.getDate() + expiresInDays);
      expiresAt = expiration.toISOString();
    }

    const apiKeyObj: APIKey = {
      keyId,
      keyHash,
      name,
      userId,
      scopes,
      createdAt: now.toISOString(),
      expiresAt,
      lastUsed: undefined,
      isActive: true,
    };

    return [apiKey, apiKeyObj];
  }

  /**
   * Verify API key
   * @param apiKey - Plain API key from request
   * @param storedKey - Stored APIKey object
   * @returns True if valid
   */
  verifyAPIKey(apiKey: string, storedKey: APIKey): boolean {
    // Check if active
    if (!storedKey.isActive) {
      return false;
    }

    // Check expiration
    if (storedKey.expiresAt) {
      const expires = new Date(storedKey.expiresAt);
      if (new Date() > expires) {
        return false;
      }
    }

    // Verify hash using timing-safe comparison
    const providedHash = Buffer.from(this.hashAPIKey(apiKey), 'hex');
    const storedHash = Buffer.from(storedKey.keyHash, 'hex');

    if (providedHash.length !== storedHash.length) {
      return false;
    }

    return timingSafeEqual(providedHash, storedHash);
  }

  /**
   * Check if API key has required scope
   * @param apiKey - APIKey object
   * @param requiredScope - Required scope
   * @returns True if scope present
   */
  hasScope(apiKey: APIKey, requiredScope: string): boolean {
    return apiKey.scopes.includes(requiredScope);
  }

  /**
   * Rotate an API key
   * @param oldKey - Existing APIKey object
   * @returns Tuple of [newPlainKey, newAPIKey]
   */
  rotateAPIKey(oldKey: APIKey): [string, APIKey] {
    return this.createAPIKey(
      oldKey.userId,
      oldKey.name,
      oldKey.scopes,
      undefined
    );
  }
}

export class APIKeyStore {
  private keys: Map<string, APIKey>;

  constructor() {
    this.keys = new Map();
  }

  /**
   * Save API key
   * @param apiKey - APIKey to save
   */
  save(apiKey: APIKey): void {
    this.keys.set(apiKey.keyId, apiKey);
  }

  /**
   * Get API key by ID
   * @param keyId - Key ID
   * @returns APIKey or undefined
   */
  getById(keyId: string): APIKey | undefined {
    return this.keys.get(keyId);
  }

  /**
   * List all keys for a user
   * @param userId - User ID
   * @returns Array of APIKeys
   */
  listUserKeys(userId: number): APIKey[] {
    return Array.from(this.keys.values()).filter(
      (key) => key.userId === userId
    );
  }

  /**
   * Revoke an API key
   * @param keyId - Key ID
   * @returns True if revoked
   */
  revoke(keyId: string): boolean {
    const key = this.keys.get(keyId);
    if (key) {
      key.isActive = false;
      return true;
    }
    return false;
  }

  /**
   * Update last used timestamp
   * @param keyId - Key ID
   */
  updateLastUsed(keyId: string): void {
    const key = this.keys.get(keyId);
    if (key) {
      key.lastUsed = new Date().toISOString();
    }
  }
}

export class APIKeyRateLimiter {
  private redis: any; // Redis client type
  private prefix: string;

  /**
   * Initialize rate limiter
   * @param redisClient - Redis client for storing counts
   * @param prefix - Redis key prefix
   */
  constructor(redisClient: any, prefix: string = 'ratelimit:') {
    this.redis = redisClient;
    this.prefix = prefix;
  }

  /**
   * Check rate limit for API key
   * @param keyId - API key ID
   * @param limit - Maximum requests per window
   * @param windowSeconds - Time window in seconds
   * @returns Tuple of [allowed, rateLimitInfo]
   */
  async checkRateLimit(
    keyId: string,
    limit: number = 1000,
    windowSeconds: number = 3600
  ): Promise<[boolean, RateLimitInfo]> {
    const currentTime = Math.floor(Date.now() / 1000);
    const windowStart = currentTime - windowSeconds;

    const redisKey = `${this.prefix}${keyId}`;

    // Remove old entries
    await this.redis.zRemRangeByScore(redisKey, 0, windowStart);

    // Count requests in current window
    const currentCount = await this.redis.zCard(redisKey);

    const rateLimitInfo: RateLimitInfo = {
      limit,
      remaining: Math.max(0, limit - currentCount),
      reset: currentTime + windowSeconds,
      used: currentCount,
    };

    if (currentCount >= limit) {
      return [false, rateLimitInfo];
    }

    // Add current request
    await this.redis.zAdd(redisKey, {
      score: currentTime,
      value: currentTime.toString(),
    });
    await this.redis.expire(redisKey, windowSeconds);

    rateLimitInfo.remaining -= 1;
    rateLimitInfo.used += 1;

    return [true, rateLimitInfo];
  }

  /**
   * Get current rate limit status
   * @param keyId - API key ID
   * @param limit - Maximum requests per window
   * @param windowSeconds - Time window in seconds
   * @returns Rate limit info
   */
  async getRateLimitStatus(
    keyId: string,
    limit: number = 1000,
    windowSeconds: number = 3600
  ): Promise<RateLimitInfo> {
    const currentTime = Math.floor(Date.now() / 1000);
    const windowStart = currentTime - windowSeconds;

    const redisKey = `${this.prefix}${keyId}`;

    // Remove old entries
    await this.redis.zRemRangeByScore(redisKey, 0, windowStart);

    // Count requests
    const currentCount = await this.redis.zCard(redisKey);

    return {
      limit,
      remaining: Math.max(0, limit - currentCount),
      reset: currentTime + windowSeconds,
      used: currentCount,
    };
  }
}

// Example usage
if (require.main === module) {
  const keyManager = new APIKeyManager('super_secret_pepper_value');

  // Create API key
  const [plainKey, apiKeyObj] = keyManager.createAPIKey(
    123,
    'Production API Key',
    ['read', 'write', 'admin'],
    365
  );

  console.log(`Generated API Key: ${plainKey}`);
  console.log(`Key ID: ${apiKeyObj.keyId}`);
  console.log(`Scopes: ${apiKeyObj.scopes.join(', ')}`);

  // Store key
  const store = new APIKeyStore();
  store.save(apiKeyObj);

  // Verify key
  const isValid = keyManager.verifyAPIKey(plainKey, apiKeyObj);
  console.log(`\nKey valid: ${isValid}`);

  // Check scope
  const hasAdmin = keyManager.hasScope(apiKeyObj, 'admin');
  console.log(`Has admin scope: ${hasAdmin}`);

  // List user keys
  const userKeys = store.listUserKeys(123);
  console.log(`\nUser has ${userKeys.length} keys`);

  // Update last used
  store.updateLastUsed(apiKeyObj.keyId);
  const updatedKey = store.getById(apiKeyObj.keyId);
  console.log(`Last used: ${updatedKey?.lastUsed}`);
}
