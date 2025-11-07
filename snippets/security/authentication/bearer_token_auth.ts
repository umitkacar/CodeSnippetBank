/**
 * Bearer Token Authentication (TypeScript)
 * Production-ready Bearer token implementation for API authentication
 */

interface User {
  user_id: number;
  username: string;
  scopes: string[];
  [key: string]: any;
}

type TokenValidator = (token: string) => Promise<User | null> | User | null;

export class BearerTokenAuth {
  private tokenValidator: TokenValidator;

  /**
   * Initialize bearer token auth
   * @param tokenValidator - Function to validate token and return user data
   */
  constructor(tokenValidator: TokenValidator) {
    this.tokenValidator = tokenValidator;
  }

  /**
   * Extract bearer token from Authorization header
   * @param authorizationHeader - Authorization header value
   * @returns Token string or null
   */
  extractToken(authorizationHeader?: string): string | null {
    if (!authorizationHeader) {
      return null;
    }

    // Bearer token format: "Bearer <token>"
    const match = authorizationHeader.match(/^Bearer\s+(.+)$/i);

    if (match) {
      return match[1];
    }

    return null;
  }

  /**
   * Authenticate request using bearer token
   * @param authorizationHeader - Authorization header value
   * @returns User data if authenticated, null otherwise
   */
  async authenticate(authorizationHeader?: string): Promise<User | null> {
    const token = this.extractToken(authorizationHeader);

    if (!token) {
      return null;
    }

    // Validate token
    return await this.tokenValidator(token);
  }

  /**
   * Check if user has required scope
   * @param user - User object
   * @param requiredScope - Required permission scope
   * @returns True if user has scope
   */
  hasScope(user: User, requiredScope: string): boolean {
    return user.scopes.includes(requiredScope);
  }

  /**
   * Check if user has any of the required scopes
   * @param user - User object
   * @param requiredScopes - Array of required scopes
   * @returns True if user has at least one scope
   */
  hasAnyScope(user: User, requiredScopes: string[]): boolean {
    return requiredScopes.some((scope) => user.scopes.includes(scope));
  }

  /**
   * Check if user has all required scopes
   * @param user - User object
   * @param requiredScopes - Array of required scopes
   * @returns True if user has all scopes
   */
  hasAllScopes(user: User, requiredScopes: string[]): boolean {
    return requiredScopes.every((scope) => user.scopes.includes(scope));
  }
}

/**
 * Express middleware for Bearer token authentication
 */
export class ExpressBearerAuth {
  private auth: BearerTokenAuth;

  constructor(tokenValidator: TokenValidator) {
    this.auth = new BearerTokenAuth(tokenValidator);
  }

  /**
   * Middleware to require authentication
   */
  requireAuth() {
    return async (req: any, res: any, next: any) => {
      const authHeader = req.headers.authorization;
      const user = await this.auth.authenticate(authHeader);

      if (!user) {
        return res.status(401).json({
          error: 'Unauthorized',
          message: 'Valid authentication required',
        });
      }

      req.user = user;
      next();
    };
  }

  /**
   * Middleware to require specific scope
   * @param requiredScope - Required permission scope
   */
  requireScope(requiredScope: string) {
    return async (req: any, res: any, next: any) => {
      const authHeader = req.headers.authorization;
      const user = await this.auth.authenticate(authHeader);

      if (!user) {
        return res.status(401).json({
          error: 'Unauthorized',
          message: 'Valid authentication required',
        });
      }

      if (!this.auth.hasScope(user, requiredScope)) {
        return res.status(403).json({
          error: 'Forbidden',
          message: 'Insufficient permissions',
        });
      }

      req.user = user;
      next();
    };
  }

  /**
   * Middleware to require any of the specified scopes
   * @param requiredScopes - Array of required scopes
   */
  requireAnyScope(requiredScopes: string[]) {
    return async (req: any, res: any, next: any) => {
      const authHeader = req.headers.authorization;
      const user = await this.auth.authenticate(authHeader);

      if (!user) {
        return res.status(401).json({
          error: 'Unauthorized',
          message: 'Valid authentication required',
        });
      }

      if (!this.auth.hasAnyScope(user, requiredScopes)) {
        return res.status(403).json({
          error: 'Forbidden',
          message: 'Insufficient permissions',
        });
      }

      req.user = user;
      next();
    };
  }
}

/**
 * FastAPI-style dependency for Bearer auth
 */
export class FastAPIBearerAuth {
  private auth: BearerTokenAuth;

  constructor(tokenValidator: TokenValidator) {
    this.auth = new BearerTokenAuth(tokenValidator);
  }

  /**
   * Get current authenticated user
   * @param authHeader - Authorization header
   * @returns User or throws error
   */
  async getCurrentUser(authHeader?: string): Promise<User> {
    const user = await this.auth.authenticate(authHeader);

    if (!user) {
      throw new Error('Unauthorized');
    }

    return user;
  }

  /**
   * Get current user with required scope
   * @param authHeader - Authorization header
   * @param requiredScope - Required scope
   * @returns User or throws error
   */
  async getCurrentUserWithScope(
    authHeader: string | undefined,
    requiredScope: string
  ): Promise<User> {
    const user = await this.getCurrentUser(authHeader);

    if (!this.auth.hasScope(user, requiredScope)) {
      throw new Error('Forbidden');
    }

    return user;
  }
}

// Example usage
if (require.main === module) {
  // Create token validator
  const validateToken = async (token: string): Promise<User | null> => {
    // In production, validate JWT or query database
    const validTokens: Record<string, User> = {
      secret_token_123: {
        user_id: 1,
        username: 'john_doe',
        scopes: ['read', 'write', 'admin'],
      },
    };

    return validTokens[token] || null;
  };

  // Initialize auth
  const auth = new BearerTokenAuth(validateToken);

  // Test authentication
  (async () => {
    const authHeader = 'Bearer secret_token_123';
    const user = await auth.authenticate(authHeader);

    if (user) {
      console.log('Authenticated:', user);
      console.log('Has admin scope:', auth.hasScope(user, 'admin'));
      console.log(
        'Has any scope:',
        auth.hasAnyScope(user, ['admin', 'superuser'])
      );
    } else {
      console.log('Authentication failed');
    }

    // Test invalid token
    const invalidUser = await auth.authenticate('Bearer invalid_token');
    console.log('Invalid token result:', invalidUser);
  })();
}
