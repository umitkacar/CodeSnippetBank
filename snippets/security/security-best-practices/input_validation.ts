/**
 * Input Validation (TypeScript)
 */
export class InputValidator {
  static validateEmail(email: string): boolean {
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return pattern.test(email);
  }

  static validatePhone(phone: string): boolean {
    const pattern = /^\+?1?\d{9,15}$/;
    return pattern.test(phone);
  }

  static sanitizeString(input: string, maxLength: number = 255): string {
    return input.replace(/[<>\"']/g, '').substring(0, maxLength).trim();
  }

  static validateUrl(url: string): boolean {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }
}
