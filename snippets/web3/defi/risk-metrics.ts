/**
 * DeFi Risk Metrics
 * Calculate and monitor risk metrics
 */

export interface RiskProfile {
  volatility: number;
  sharpeRatio: number;
  maxDrawdown: number;
  valueAtRisk: number;
  liquidationRisk: number;
}

// Calculate volatility
export function calculateVolatility(prices: number[]): number {
  if (prices.length < 2) return 0;

  const returns = [];
  for (let i = 1; i < prices.length; i++) {
    returns.push((prices[i] - prices[i - 1]) / prices[i - 1]);
  }

  const mean = returns.reduce((a, b) => a + b) / returns.length;
  const squaredDiffs = returns.map((r) => Math.pow(r - mean, 2));
  const variance = squaredDiffs.reduce((a, b) => a + b) / squaredDiffs.length;

  return Math.sqrt(variance) * Math.sqrt(365) * 100; // Annualized
}

// Calculate Sharpe Ratio
export function calculateSharpeRatio(
  returns: number[],
  riskFreeRate: number = 2
): number {
  const avgReturn =
    returns.reduce((a, b) => a + b, 0) / returns.length;
  const excessReturn = avgReturn - riskFreeRate / 100;

  const variance =
    returns
      .map((r) => Math.pow(r - avgReturn, 2))
      .reduce((a, b) => a + b) / returns.length;

  const stdDev = Math.sqrt(variance);

  return excessReturn / stdDev;
}

// Calculate Maximum Drawdown
export function calculateMaxDrawdown(values: number[]): number {
  let maxDrawdown = 0;
  let peak = values[0];

  for (const value of values) {
    if (value > peak) {
      peak = value;
    }

    const drawdown = ((peak - value) / peak) * 100;
    if (drawdown > maxDrawdown) {
      maxDrawdown = drawdown;
    }
  }

  return maxDrawdown;
}

// Value at Risk (VaR) - 95% confidence
export function calculateVaR(
  portfolioValue: number,
  volatility: number,
  confidence: number = 1.65 // 95% confidence
): number {
  return portfolioValue * volatility * confidence;
}

// Liquidation risk score
export function calculateLiquidationRisk(
  healthFactor: number,
  volatility: number
): number {
  if (healthFactor >= 2) return 0; // Very safe

  const baseRisk = Math.max(0, (2 - healthFactor) / 2) * 100;
  const volatilityAdjustment = volatility / 10;

  return Math.min(100, baseRisk + volatilityAdjustment);
}

// Portfolio correlation
export function calculateCorrelation(
  asset1Returns: number[],
  asset2Returns: number[]
): number {
  if (asset1Returns.length !== asset2Returns.length) {
    throw new Error('Arrays must have equal length');
  }

  const n = asset1Returns.length;
  const mean1 = asset1Returns.reduce((a, b) => a + b) / n;
  const mean2 = asset2Returns.reduce((a, b) => a + b) / n;

  let numerator = 0;
  let sum1Sq = 0;
  let sum2Sq = 0;

  for (let i = 0; i < n; i++) {
    const diff1 = asset1Returns[i] - mean1;
    const diff2 = asset2Returns[i] - mean2;

    numerator += diff1 * diff2;
    sum1Sq += diff1 * diff1;
    sum2Sq += diff2 * diff2;
  }

  return numerator / Math.sqrt(sum1Sq * sum2Sq);
}

// Diversification score
export function calculateDiversification(
  correlations: number[]
): number {
  const avgCorrelation =
    correlations.reduce((a, b) => a + b, 0) / correlations.length;

  return (1 - avgCorrelation) * 100;
}

// Risk assessment
export function assessRisk(profile: RiskProfile): {
  score: number;
  level: 'low' | 'medium' | 'high' | 'extreme';
  recommendations: string[];
} {
  let score = 0;
  const recommendations: string[] = [];

  // Volatility score (0-25)
  score += Math.min(25, (profile.volatility / 100) * 25);
  if (profile.volatility > 50) {
    recommendations.push('High volatility - consider reducing position sizes');
  }

  // Sharpe ratio score (0-25, inverse)
  score += Math.min(25, Math.max(0, (2 - profile.sharpeRatio) * 12.5));
  if (profile.sharpeRatio < 1) {
    recommendations.push('Poor risk-adjusted returns');
  }

  // Max drawdown score (0-25)
  score += Math.min(25, (profile.maxDrawdown / 50) * 25);
  if (profile.maxDrawdown > 30) {
    recommendations.push('Large drawdowns detected - review position sizing');
  }

  // Liquidation risk score (0-25)
  score += Math.min(25, (profile.liquidationRisk / 100) * 25);
  if (profile.liquidationRisk > 50) {
    recommendations.push('High liquidation risk - add collateral or reduce debt');
  }

  let level: 'low' | 'medium' | 'high' | 'extreme';
  if (score < 25) level = 'low';
  else if (score < 50) level = 'medium';
  else if (score < 75) level = 'high';
  else level = 'extreme';

  return { score, level, recommendations };
}

export default {
  calculateVolatility,
  calculateSharpeRatio,
  calculateMaxDrawdown,
  calculateVaR,
  calculateLiquidationRisk,
  calculateCorrelation,
  calculateDiversification,
  assessRisk,
};
