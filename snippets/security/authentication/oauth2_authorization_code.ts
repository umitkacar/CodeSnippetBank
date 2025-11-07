/**
 * OAuth2 Authorization Code Flow Implementation (TypeScript)
 * Production-ready OAuth2 with PKCE support
 */
import { randomBytes, createHash } from 'crypto';
import axios, { AxiosError } from 'axios';

interface OAuth2Config {
  clientId: string;
  clientSecret: string;
  authorizationUrl: string;
  tokenUrl: string;
  redirectUri: string;
  scope?: string;
}

interface PKCEPair {
  codeVerifier: string;
  codeChallenge: string;
}

interface SessionData {
  state: string;
  codeVerifier?: string;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token?: string;
  scope?: string;
}

export class OAuth2Client {
  private config: Required<OAuth2Config>;

  constructor(config: OAuth2Config) {
    this.config = {
      ...config,
      scope: config.scope || 'openid profile email',
    };
  }

  /**
   * Generate PKCE code verifier and challenge
   * @returns Object with code verifier and challenge
   */
  generatePKCEPair(): PKCEPair {
    // Generate code verifier (43-128 characters)
    const codeVerifier = randomBytes(32)
      .toString('base64url');

    // Generate code challenge (SHA256 hash of verifier)
    const codeChallenge = createHash('sha256')
      .update(codeVerifier)
      .digest('base64url');

    return { codeVerifier, codeChallenge };
  }

  /**
   * Generate authorization URL
   * @param state - Optional state for CSRF protection
   * @param usePKCE - Whether to use PKCE
   * @returns Authorization URL and session data
   */
  getAuthorizationUrl(
    state?: string,
    usePKCE: boolean = true
  ): { url: string; sessionData: SessionData } {
    const stateValue = state || randomBytes(32).toString('base64url');
    const sessionData: SessionData = { state: stateValue };

    const params = new URLSearchParams({
      client_id: this.config.clientId,
      redirect_uri: this.config.redirectUri,
      response_type: 'code',
      scope: this.config.scope,
      state: stateValue,
    });

    if (usePKCE) {
      const { codeVerifier, codeChallenge } = this.generatePKCEPair();
      params.append('code_challenge', codeChallenge);
      params.append('code_challenge_method', 'S256');
      sessionData.codeVerifier = codeVerifier;
    }

    const url = `${this.config.authorizationUrl}?${params.toString()}`;
    return { url, sessionData };
  }

  /**
   * Exchange authorization code for access token
   * @param code - Authorization code from callback
   * @param codeVerifier - PKCE code verifier if used
   * @returns Token response
   */
  async exchangeCodeForToken(
    code: string,
    codeVerifier?: string
  ): Promise<TokenResponse | null> {
    const data = new URLSearchParams({
      grant_type: 'authorization_code',
      code,
      redirect_uri: this.config.redirectUri,
      client_id: this.config.clientId,
      client_secret: this.config.clientSecret,
    });

    if (codeVerifier) {
      data.append('code_verifier', codeVerifier);
    }

    try {
      const response = await axios.post<TokenResponse>(
        this.config.tokenUrl,
        data.toString(),
        {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          timeout: 10000,
        }
      );

      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        console.error('Token exchange failed:', error.message);
      }
      return null;
    }
  }

  /**
   * Refresh access token using refresh token
   * @param refreshToken - Refresh token
   * @returns New token response
   */
  async refreshAccessToken(
    refreshToken: string
  ): Promise<TokenResponse | null> {
    const data = new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: refreshToken,
      client_id: this.config.clientId,
      client_secret: this.config.clientSecret,
    });

    try {
      const response = await axios.post<TokenResponse>(
        this.config.tokenUrl,
        data.toString(),
        { timeout: 10000 }
      );

      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        console.error('Token refresh failed:', error.message);
      }
      return null;
    }
  }

  /**
   * Revoke access or refresh token
   * @param token - Token to revoke
   * @param tokenTypeHint - Type of token
   * @returns True if successful
   */
  async revokeToken(
    token: string,
    tokenTypeHint: 'access_token' | 'refresh_token' = 'access_token'
  ): Promise<boolean> {
    const revocationUrl = this.config.tokenUrl.replace('/token', '/revoke');

    const data = new URLSearchParams({
      token,
      token_type_hint: tokenTypeHint,
      client_id: this.config.clientId,
      client_secret: this.config.clientSecret,
    });

    try {
      await axios.post(revocationUrl, data.toString(), { timeout: 10000 });
      return true;
    } catch {
      return false;
    }
  }
}

// Example usage
if (require.main === module) {
  const oauthClient = new OAuth2Client({
    clientId: 'your_client_id',
    clientSecret: 'your_client_secret',
    authorizationUrl: 'https://provider.com/oauth/authorize',
    tokenUrl: 'https://provider.com/oauth/token',
    redirectUri: 'https://yourapp.com/callback',
  });

  // Step 1: Get authorization URL
  const { url, sessionData } = oauthClient.getAuthorizationUrl(undefined, true);
  console.log('Authorization URL:', url);
  console.log('Session data:', sessionData);
}
