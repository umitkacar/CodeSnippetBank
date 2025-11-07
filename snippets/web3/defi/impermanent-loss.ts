/**
 * Impermanent Loss Calculator
 * Calculate and visualize IL for liquidity providers
 */

export interface ILResult {
  impermanentLoss: number;
  impermanentLossPercentage: number;
  hodlValue: number;
  lpValue: number;
  feesEarned?: number;
  netResult?: number;
}

// Calculate impermanent loss
export function calculateImpermanentLoss(
  initialPriceA: number,
  initialPriceB: number,
  currentPriceA: number,
  currentPriceB: number,
  initialAmountA: number,
  initialAmountB: number
): ILResult {
  // Initial value
  const initialValue =
    initialAmountA * initialPriceA + initialAmountB * initialPriceB;

  // HODL value
  const hodlValue =
    initialAmountA * currentPriceA + initialAmountB * currentPriceB;

  // Price ratio change
  const priceRatio = (currentPriceA / currentPriceB) / (initialPriceA / initialPriceB);

  // LP value (constant product formula)
  const lpMultiplier = (2 * Math.sqrt(priceRatio)) / (1 + priceRatio);
  const lpValue = initialValue * lpMultiplier * (currentPriceA / initialPriceA);

  // Impermanent loss
  const impermanentLoss = hodlValue - lpValue;
  const impermanentLossPercentage = (impermanentLoss / hodlValue) * 100;

  return {
    impermanentLoss,
    impermanentLossPercentage,
    hodlValue,
    lpValue,
  };
}

// Calculate IL by price change
export function calculateILByPriceChange(
  priceChangePercentage: number
): number {
  const priceRatio = 1 + priceChangePercentage / 100;
  const ilMultiplier = (2 * Math.sqrt(priceRatio)) / (1 + priceRatio);

  return (1 - ilMultiplier) * 100;
}

// Minimum fees to offset IL
export function calculateBreakEvenFees(
  impermanentLossPercentage: number
): number {
  return Math.abs(impermanentLossPercentage);
}

// Time to break even
export function calculateTimeToBreakEven(
  impermanentLossPercentage: number,
  dailyFeeAPR: number
): number {
  if (dailyFeeAPR <= 0) return Infinity;

  const dailyFeePercentage = dailyFeeAPR / 365;
  return Math.abs(impermanentLossPercentage) / dailyFeePercentage;
}

// IL with fee earnings
export function calculateNetResult(
  ilResult: ILResult,
  feesEarned: number
): ILResult {
  const netResult = feesEarned - ilResult.impermanentLoss;

  return {
    ...ilResult,
    feesEarned,
    netResult,
  };
}

// IL range calculator
export function calculateILRange(
  priceChanges: number[]
): Array<{ priceChange: number; il: number }> {
  return priceChanges.map((change) => ({
    priceChange: change,
    il: calculateILByPriceChange(change),
  }));
}

// Standard IL benchmarks
export const IL_BENCHMARKS = [
  { priceChange: 25, il: 0.6 },
  { priceChange: 50, il: 2.0 },
  { priceChange: 75, il: 3.8 },
  { priceChange: 100, il: 5.7 },
  { priceChange: 200, il: 13.4 },
  { priceChange: 300, il: 20.0 },
  { priceChange: 400, il: 25.5 },
  { priceChange: 500, il: 30.3 },
];

export default {
  calculateImpermanentLoss,
  calculateILByPriceChange,
  calculateBreakEvenFees,
  calculateTimeToBreakEven,
  calculateNetResult,
  calculateILRange,
  IL_BENCHMARKS,
};
