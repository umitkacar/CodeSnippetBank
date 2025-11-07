/**
 * Multi-Factor Authentication (TOTP) Implementation (TypeScript)
 * Production-ready 2FA with Time-based One-Time Password
 */
import * as speakeasy from 'speakeasy';
import * as QRCode from 'qrcode';
import { randomBytes } from 'crypto';

interface TOTPSecret {
  secret: string;
  qrCodeUrl: string;
  backupCodes: string[];
}

interface TOTPVerification {
  isValid: boolean;
  delta?: number;
}

export class TOTPAuthenticator {
  private issuerName: string;

  /**
   * Initialize TOTP authenticator
   * @param issuerName - Application name
   */
  constructor(issuerName: string = 'MyApp') {
    this.issuerName = issuerName;
  }

  /**
   * Generate a new TOTP secret
   * @returns Base32-encoded secret key
   */
  generateSecret(): string {
    const secret = speakeasy.generateSecret({
      length: 32,
      name: this.issuerName,
    });

    return secret.base32;
  }

  /**
   * Get provisioning URI for QR code
   * @param secret - TOTP secret key
   * @param userIdentifier - User email or username
   * @param issuerName - Optional issuer name override
   * @returns Provisioning URI
   */
  getProvisioningUri(
    secret: string,
    userIdentifier: string,
    issuerName?: string
  ): string {
    return speakeasy.otpauthURL({
      secret,
      label: userIdentifier,
      issuer: issuerName || this.issuerName,
      encoding: 'base32',
    });
  }

  /**
   * Generate QR code as data URL
   * @param secret - TOTP secret key
   * @param userIdentifier - User email or username
   * @returns Base64-encoded QR code image
   */
  async generateQRCode(
    secret: string,
    userIdentifier: string
  ): Promise<string> {
    const uri = this.getProvisioningUri(secret, userIdentifier);

    try {
      const qrCodeDataUrl = await QRCode.toDataURL(uri);
      return qrCodeDataUrl;
    } catch (error) {
      console.error('QR code generation error:', error);
      throw new Error('Failed to generate QR code');
    }
  }

  /**
   * Verify TOTP token
   * @param secret - TOTP secret key
   * @param token - 6-digit TOTP code from user
   * @param validWindow - Number of time steps to check (default 1 = 30s window)
   * @returns Verification result
   */
  verifyToken(
    secret: string,
    token: string,
    validWindow: number = 1
  ): TOTPVerification {
    const result = speakeasy.totp.verify({
      secret,
      encoding: 'base32',
      token,
      window: validWindow,
    });

    if (typeof result === 'boolean') {
      return { isValid: result };
    }

    // Some versions return delta
    return {
      isValid: true,
      delta: result as number,
    };
  }

  /**
   * Get current TOTP token (for testing)
   * @param secret - TOTP secret key
   * @returns Current 6-digit token
   */
  getCurrentToken(secret: string): string {
    return speakeasy.totp({
      secret,
      encoding: 'base32',
    });
  }

  /**
   * Get seconds remaining until next token
   * @returns Seconds until token expires
   */
  getTimeRemaining(): number {
    const now = Math.floor(Date.now() / 1000);
    return 30 - (now % 30);
  }

  /**
   * Setup 2FA for a user
   * @param userIdentifier - User email or username
   * @returns TOTP setup data
   */
  async setupTOTP(userIdentifier: string): Promise<TOTPSecret> {
    const secret = this.generateSecret();
    const qrCodeUrl = await this.generateQRCode(secret, userIdentifier);
    const backupCodes = BackupCodes.generateBackupCodes();

    return {
      secret,
      qrCodeUrl,
      backupCodes,
    };
  }
}

export class BackupCodes {
  /**
   * Generate backup recovery codes
   * @param count - Number of codes to generate
   * @returns Array of backup codes
   */
  static generateBackupCodes(count: number = 10): string[] {
    const codes: string[] = [];
    const charset = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';

    for (let i = 0; i < count; i++) {
      let code = '';
      const randomValues = randomBytes(8);

      for (let j = 0; j < 8; j++) {
        code += charset[randomValues[j] % charset.length];
      }

      // Format as XXXX-XXXX for readability
      const formatted = `${code.substring(0, 4)}-${code.substring(4)}`;
      codes.push(formatted);
    }

    return codes;
  }

  /**
   * Hash backup code for storage
   * @param code - Plain backup code
   * @returns Hashed code
   */
  static hashBackupCode(code: string): string {
    const { createHash } = require('crypto');
    return createHash('sha256').update(code).digest('hex');
  }

  /**
   * Verify backup code
   * @param code - Plain code from user
   * @param hashedCode - Stored hashed code
   * @returns True if code matches
   */
  static verifyBackupCode(code: string, hashedCode: string): boolean {
    const { createHash, timingSafeEqual } = require('crypto');
    const hash = createHash('sha256').update(code).digest();
    const storedHash = Buffer.from(hashedCode, 'hex');

    if (hash.length !== storedHash.length) {
      return false;
    }

    return timingSafeEqual(hash, storedHash);
  }
}

export class MFAManager {
  private authenticator: TOTPAuthenticator;
  private mfaData: Map<number, MFAUserData>;

  constructor(issuerName: string = 'MyApp') {
    this.authenticator = new TOTPAuthenticator(issuerName);
    this.mfaData = new Map();
  }

  /**
   * Enable MFA for a user
   * @param userId - User ID
   * @param userIdentifier - User email/username
   * @returns TOTP setup data
   */
  async enableMFA(
    userId: number,
    userIdentifier: string
  ): Promise<TOTPSecret> {
    const setup = await this.authenticator.setupTOTP(userIdentifier);

    // Store MFA data (in production, save to database)
    const backupCodesHashed = setup.backupCodes.map((code) =>
      BackupCodes.hashBackupCode(code)
    );

    this.mfaData.set(userId, {
      secret: setup.secret,
      backupCodes: backupCodesHashed,
      isEnabled: false, // Enable after verification
      createdAt: new Date().toISOString(),
    });

    return setup;
  }

  /**
   * Verify and activate MFA
   * @param userId - User ID
   * @param token - TOTP token
   * @returns True if verified and activated
   */
  verifyAndActivate(userId: number, token: string): boolean {
    const userData = this.mfaData.get(userId);

    if (!userData) {
      return false;
    }

    const verification = this.authenticator.verifyToken(
      userData.secret,
      token
    );

    if (verification.isValid) {
      userData.isEnabled = true;
      return true;
    }

    return false;
  }

  /**
   * Verify MFA code
   * @param userId - User ID
   * @param code - TOTP or backup code
   * @returns True if valid
   */
  verifyMFA(userId: number, code: string): boolean {
    const userData = this.mfaData.get(userId);

    if (!userData || !userData.isEnabled) {
      return false;
    }

    // Try TOTP first
    const totpVerification = this.authenticator.verifyToken(
      userData.secret,
      code
    );

    if (totpVerification.isValid) {
      return true;
    }

    // Try backup codes
    for (let i = 0; i < userData.backupCodes.length; i++) {
      if (BackupCodes.verifyBackupCode(code, userData.backupCodes[i])) {
        // Remove used backup code
        userData.backupCodes.splice(i, 1);
        return true;
      }
    }

    return false;
  }

  /**
   * Disable MFA for a user
   * @param userId - User ID
   * @returns True if disabled
   */
  disableMFA(userId: number): boolean {
    return this.mfaData.delete(userId);
  }

  /**
   * Check if MFA is enabled for user
   * @param userId - User ID
   * @returns True if enabled
   */
  isMFAEnabled(userId: number): boolean {
    const userData = this.mfaData.get(userId);
    return userData?.isEnabled || false;
  }
}

interface MFAUserData {
  secret: string;
  backupCodes: string[];
  isEnabled: boolean;
  createdAt: string;
}

// Example usage
if (require.main === module) {
  (async () => {
    const authenticator = new TOTPAuthenticator('MySecureApp');

    // Setup 2FA for a user
    const userEmail = 'user@example.com';
    const setup = await authenticator.setupTOTP(userEmail);

    console.log('Secret key:', setup.secret);
    console.log('QR Code:', setup.qrCodeUrl.substring(0, 50) + '...');
    console.log('Backup codes:', setup.backupCodes);

    // Get current token (for testing)
    const currentToken = authenticator.getCurrentToken(setup.secret);
    console.log('\nCurrent token:', currentToken);

    // Verify token
    const verification = authenticator.verifyToken(setup.secret, currentToken);
    console.log('Token valid:', verification.isValid);

    // Test MFA Manager
    const mfaManager = new MFAManager('MySecureApp');

    const userId = 123;
    const mfaSetup = await mfaManager.enableMFA(userId, userEmail);
    console.log('\n✓ MFA enabled for user');

    // Verify and activate
    const testToken = authenticator.getCurrentToken(mfaSetup.secret);
    const activated = mfaManager.verifyAndActivate(userId, testToken);
    console.log('MFA activated:', activated);

    // Verify MFA
    const verified = mfaManager.verifyMFA(userId, testToken);
    console.log('MFA verified:', verified);
  })();
}
