/**
 * Slippage Protection
 * Calculate and protect against slippage
 */

export interface SlippageConfig {
  tolerance: number; // Percentage (e.g., 0.5 for 0.5%)
  deadline: number; // Seconds
  maxPriceImpact: number; // Percentage
}

// Calculate minimum amount out
export function calculateMinAmountOut(
  expectedAmount: bigint,
  slippageTolerance: number
): bigint {
  const slippageBps = BigInt(Math.floor(slippageTolerance * 100));
  return (expectedAmount * (10000n - slippageBps)) / 10000n;
}

// Calculate maximum amount in
export function calculateMaxAmountIn(
  expectedAmount: bigint,
  slippageTolerance: number
): bigint {
  const slippageBps = BigInt(Math.floor(slippageTolerance * 100));
  return (expectedAmount * (10000n + slippageBps)) / 10000n;
}

// Calculate price impact
export function calculatePriceImpact(
  inputReserve: bigint,
  outputReserve: bigint,
  inputAmount: bigint,
  outputAmount: bigint
): number {
  // Effective price
  const effectivePrice = Number(inputAmount) / Number(outputAmount);

  // Market price
  const marketPrice = Number(inputReserve) / Number(outputReserve);

  // Price impact
  return ((effectivePrice - marketPrice) / marketPrice) * 100;
}

// Check if trade is safe
export function isTradeSafe(
  priceImpact: number,
  slippageTolerance: number,
  maxPriceImpact: number = 5
): { safe: boolean; warnings: string[] } {
  const warnings: string[] = [];

  if (priceImpact > maxPriceImpact) {
    warnings.push(`High price impact: ${priceImpact.toFixed(2)}%`);
  }

  if (priceImpact > slippageTolerance * 2) {
    warnings.push('Price impact exceeds 2x slippage tolerance');
  }

  if (priceImpact > 10) {
    warnings.push('Extremely high price impact - trade not recommended');
  }

  return {
    safe: warnings.length === 0,
    warnings,
  };
}

// Calculate deadline timestamp
export function calculateDeadline(minutes: number = 20): number {
  return Math.floor(Date.now() / 1000) + minutes * 60;
}

// Optimal slippage for trade size
export function getOptimalSlippage(
  tradeSize: bigint,
  liquidity: bigint
): number {
  const tradeSizePercentage = Number((tradeSize * 10000n) / liquidity) / 100;

  if (tradeSizePercentage < 0.1) return 0.1; // 0.1%
  if (tradeSizePercentage < 0.5) return 0.5; // 0.5%
  if (tradeSizePercentage < 1) return 1.0; // 1%
  if (tradeSizePercentage < 2) return 2.0; // 2%

  return 5.0; // 5% for large trades
}

// Split large trades to reduce slippage
export function calculateTradeChunks(
  totalAmount: bigint,
  liquidity: bigint,
  maxImpact: number = 2
): bigint[] {
  const chunks: bigint[] = [];
  let remaining = totalAmount;

  // Calculate safe chunk size (roughly 1% of liquidity)
  const safeChunkSize = liquidity / 100n;

  while (remaining > 0n) {
    const chunk = remaining < safeChunkSize ? remaining : safeChunkSize;
    chunks.push(chunk);
    remaining -= chunk;
  }

  return chunks;
}

export default {
  calculateMinAmountOut,
  calculateMaxAmountIn,
  calculatePriceImpact,
  isTradeSafe,
  calculateDeadline,
  getOptimalSlippage,
  calculateTradeChunks,
};
