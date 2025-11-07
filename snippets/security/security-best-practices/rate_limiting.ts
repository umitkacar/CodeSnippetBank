/**
 * Rate Limiting (TypeScript)
 */
export class RateLimiter {
  private requests: Map<string, number[]>;
  private maxRequests: number;
  private windowSeconds: number;

  constructor(maxRequests: number = 100, windowSeconds: number = 60) {
    this.requests = new Map();
    this.maxRequests = maxRequests;
    this.windowSeconds = windowSeconds;
  }

  isAllowed(identifier: string): {
    allowed: boolean;
    limit: number;
    remaining: number;
    reset?: number;
  } {
    const now = Date.now() / 1000;
    const windowStart = now - this.windowSeconds;

    let userRequests = this.requests.get(identifier) || [];
    userRequests = userRequests.filter((time) => time > windowStart);

    if (userRequests.length >= this.maxRequests) {
      return {
        allowed: false,
        limit: this.maxRequests,
        remaining: 0,
        reset: Math.floor(userRequests[0] + this.windowSeconds),
      };
    }

    userRequests.push(now);
    this.requests.set(identifier, userRequests);

    return {
      allowed: true,
      limit: this.maxRequests,
      remaining: this.maxRequests - userRequests.length,
    };
  }
}
