/**
 * Password Hashing with bcrypt (TypeScript)
 * Production-ready password hashing and verification
 */
import * as bcrypt from 'bcrypt';

interface PasswordStrength {
  length: number;
  hasLowercase: boolean;
  hasUppercase: boolean;
  hasDigit: boolean;
  hasSpecial: boolean;
  score: number;
  isStrong: boolean;
}

export class BcryptPasswordManager {
  private rounds: number;

  /**
   * Initialize password manager
   * @param rounds - Cost factor (4-31, default 12)
   */
  constructor(rounds: number = 12) {
    if (rounds < 4 || rounds > 31) {
      throw new Error('Rounds must be between 4 and 31');
    }
    this.rounds = rounds;
  }

  /**
   * Hash a password
   * @param password - Plain text password
   * @returns Hashed password (includes salt)
   */
  async hashPassword(password: string): Promise<string> {
    const salt = await bcrypt.genSalt(this.rounds);
    const hashed = await bcrypt.hash(password, salt);
    return hashed;
  }

  /**
   * Verify a password against its hash
   * @param password - Plain text password to verify
   * @param hashedPassword - Stored hash
   * @returns True if password matches
   */
  async verifyPassword(
    password: string,
    hashedPassword: string
  ): Promise<boolean> {
    try {
      return await bcrypt.compare(password, hashedPassword);
    } catch (error) {
      console.error('Verification error:', error);
      return false;
    }
  }

  /**
   * Check if password needs rehashing
   * @param hashedPassword - Stored hash
   * @returns True if rehash needed
   */
  needsRehash(hashedPassword: string): boolean {
    try {
      // Extract rounds from hash ($2b$rounds$...)
      const parts = hashedPassword.split('$');
      if (parts.length >= 3) {
        const currentRounds = parseInt(parts[2], 10);
        return currentRounds !== this.rounds;
      }
      return true;
    } catch {
      return true;
    }
  }

  /**
   * Update password hash if needed
   * @param password - Plain text password
   * @param oldHash - Current hash
   * @returns New hash if update needed, null otherwise
   */
  async updatePassword(
    password: string,
    oldHash: string
  ): Promise<string | null> {
    const isValid = await this.verifyPassword(password, oldHash);

    if (isValid && this.needsRehash(oldHash)) {
      return await this.hashPassword(password);
    }

    return null;
  }
}

export class PasswordStrengthValidator {
  /**
   * Check password strength
   * @param password - Password to check
   * @returns Strength metrics
   */
  static checkStrength(password: string): PasswordStrength {
    const strength: PasswordStrength = {
      length: password.length,
      hasLowercase: /[a-z]/.test(password),
      hasUppercase: /[A-Z]/.test(password),
      hasDigit: /\d/.test(password),
      hasSpecial: /[!@#$%^&*(),.?":{}|<>]/.test(password),
      score: 0,
      isStrong: false,
    };

    // Calculate score
    if (strength.length >= 8) strength.score += 1;
    if (strength.length >= 12) strength.score += 1;
    if (strength.length >= 16) strength.score += 1;

    strength.score +=
      Number(strength.hasLowercase) +
      Number(strength.hasUppercase) +
      Number(strength.hasDigit) +
      Number(strength.hasSpecial);

    // Strong password: length >= 12 and at least 3 character types
    const charTypes =
      Number(strength.hasLowercase) +
      Number(strength.hasUppercase) +
      Number(strength.hasDigit) +
      Number(strength.hasSpecial);

    strength.isStrong = strength.length >= 12 && charTypes >= 3;

    return strength;
  }

  /**
   * Validate password meets requirements
   * @param password - Password to validate
   * @param minLength - Minimum length required
   * @returns Validation result
   */
  static validatePassword(
    password: string,
    minLength: number = 12
  ): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (password.length < minLength) {
      errors.push(`Password must be at least ${minLength} characters`);
    }

    const strength = this.checkStrength(password);

    if (!strength.hasUppercase) {
      errors.push('Password must contain uppercase letters');
    }

    if (!strength.hasLowercase) {
      errors.push('Password must contain lowercase letters');
    }

    if (!strength.hasDigit) {
      errors.push('Password must contain digits');
    }

    if (!strength.hasSpecial) {
      errors.push('Password must contain special characters');
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  /**
   * Check if password is commonly used
   * @param password - Password to check
   * @returns True if common
   */
  static isCommonPassword(password: string): boolean {
    const commonPasswords = [
      'password',
      '123456',
      'qwerty',
      'admin',
      'letmein',
      'welcome',
      'monkey',
      'dragon',
      'master',
      'sunshine',
    ];

    return commonPasswords.includes(password.toLowerCase());
  }
}

// Example usage
if (require.main === module) {
  (async () => {
    const pwdManager = new BcryptPasswordManager(12);

    // Hash a password
    const password = 'SecureP@ssw0rd123';
    console.log(`Original: ${password}`);

    const hashed = await pwdManager.hashPassword(password);
    console.log(`Hashed: ${hashed}`);

    // Verify password
    const isValid = await pwdManager.verifyPassword(password, hashed);
    console.log(`Password valid: ${isValid}`);

    // Verify wrong password
    const isInvalid = await pwdManager.verifyPassword('WrongPassword', hashed);
    console.log(`Wrong password valid: ${isInvalid}`);

    // Check password strength
    const strength = PasswordStrengthValidator.checkStrength(password);
    console.log('\nPassword strength:', strength);

    // Validate password
    const validation = PasswordStrengthValidator.validatePassword(password);
    console.log(`Validation: ${validation.isValid}`);
    if (validation.errors.length > 0) {
      console.log('Errors:', validation.errors);
    }

    // Test weak password
    const weakPassword = 'weak';
    const weakValidation =
      PasswordStrengthValidator.validatePassword(weakPassword);
    console.log(`\nWeak password validation: ${weakValidation.isValid}`);
    console.log('Errors:', weakValidation.errors);
  })();
}
