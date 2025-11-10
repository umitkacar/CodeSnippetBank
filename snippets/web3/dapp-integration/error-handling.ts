/**
 * Web3 Error Handling
 * Parse and handle common Web3 errors
 */

import { useState } from 'react';
import { BaseError, ContractFunctionRevertedError } from 'viem';

export interface ParsedError {
  type: string;
  message: string;
  code?: number;
  details?: any;
}

// Parse contract revert errors
export function parseContractError(error: unknown): ParsedError {
  if (error instanceof BaseError) {
    const revertError = error.walk((err) => err instanceof ContractFunctionRevertedError);

    if (revertError instanceof ContractFunctionRevertedError) {
      const errorName = revertError.data?.errorName ?? '';
      return {
        type: 'CONTRACT_REVERT',
        message: `Contract reverted: ${errorName}`,
        details: revertError.data,
      };
    }
  }

  if (error instanceof Error) {
    return {
      type: 'GENERIC_ERROR',
      message: error.message,
    };
  }

  return {
    type: 'UNKNOWN_ERROR',
    message: 'An unknown error occurred',
  };
}

// User-friendly error messages
export function getUserFriendlyError(error: unknown): string {
  const parsed = parseContractError(error);

  // Common error patterns
  if (parsed.message.includes('insufficient funds')) {
    return 'Insufficient balance to complete transaction';
  }

  if (parsed.message.includes('user rejected')) {
    return 'Transaction was rejected';
  }

  if (parsed.message.includes('nonce too low')) {
    return 'Transaction nonce error. Please try again';
  }

  if (parsed.message.includes('gas')) {
    return 'Transaction may fail or require more gas';
  }

  if (parsed.message.includes('allowance')) {
    return 'Token allowance too low. Please approve first';
  }

  if (parsed.message.includes('MAX_SUPPLY')) {
    return 'Maximum supply reached';
  }

  if (parsed.message.includes('PAUSED')) {
    return 'Contract is currently paused';
  }

  if (parsed.message.includes('NOT_AUTHORIZED') || parsed.message.includes('Ownable')) {
    return 'You are not authorized for this action';
  }

  return parsed.message;
}

// Error hook for React components
export function useWeb3Error() {
  const [error, setError] = useState<ParsedError | null>(null);

  const handleError = (err: unknown) => {
    const parsed = parseContractError(err);
    setError(parsed);
  };

  const clearError = () => {
    setError(null);
  };

  const getUserMessage = () => {
    return error ? getUserFriendlyError(error) : null;
  };

  return {
    error,
    handleError,
    clearError,
    getUserMessage,
  };
}

// Error boundary component
export function ErrorDisplay({ error }: { error: unknown }) {
  const message = getUserFriendlyError(error);

  return (
    <div
      style={{
        padding: '16px',
        backgroundColor: '#fee2e2',
        border: '1px solid #ef4444',
        borderRadius: '8px',
        color: '#991b1b',
      }}
    >
      <strong>Error:</strong> {message}
    </div>
  );
}

// Retry with exponential backoff
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxRetries - 1) {
        throw error;
      }

      const delay = baseDelay * Math.pow(2, attempt);
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }

  throw new Error('Max retries exceeded');
}

// Transaction error codes
export const TX_ERROR_CODES = {
  USER_REJECTED: 4001,
  UNAUTHORIZED: 4100,
  UNSUPPORTED_METHOD: 4200,
  DISCONNECTED: 4900,
  CHAIN_DISCONNECTED: 4901,
};

// Check if error is user rejection
export function isUserRejection(error: any): boolean {
  return (
    error?.code === TX_ERROR_CODES.USER_REJECTED ||
    error?.message?.toLowerCase().includes('user rejected') ||
    error?.message?.toLowerCase().includes('user denied')
  );
}

// Check if error is network related
export function isNetworkError(error: any): boolean {
  return (
    error?.code === TX_ERROR_CODES.DISCONNECTED ||
    error?.code === TX_ERROR_CODES.CHAIN_DISCONNECTED ||
    error?.message?.toLowerCase().includes('network') ||
    error?.message?.toLowerCase().includes('rpc')
  );
}

export default {
  parseContractError,
  getUserFriendlyError,
  useWeb3Error,
  ErrorDisplay,
  retryWithBackoff,
  isUserRejection,
  isNetworkError,
  TX_ERROR_CODES,
};
