/**
 * Portfolio Rebalancing
 * Automated portfolio rebalancing strategies
 */

export interface Asset {
  symbol: string;
  currentValue: number;
  targetPercentage: number;
  currentPercentage: number;
}

export interface RebalanceAction {
  asset: string;
  action: 'buy' | 'sell';
  amount: number;
  percentage: number;
}

// Calculate rebalancing actions
export function calculateRebalance(
  portfolio: Asset[],
  totalValue: number,
  threshold: number = 5 // 5% deviation threshold
): RebalanceAction[] {
  const actions: RebalanceAction[] = [];

  for (const asset of portfolio) {
    const deviation = Math.abs(
      asset.currentPercentage - asset.targetPercentage
    );

    if (deviation >= threshold) {
      const targetValue = (totalValue * asset.targetPercentage) / 100;
      const difference = targetValue - asset.currentValue;

      actions.push({
        asset: asset.symbol,
        action: difference > 0 ? 'buy' : 'sell',
        amount: Math.abs(difference),
        percentage: asset.targetPercentage,
      });
    }
  }

  return actions;
}

// Check if rebalancing is needed
export function needsRebalancing(
  portfolio: Asset[],
  threshold: number = 5
): boolean {
  return portfolio.some(
    (asset) =>
      Math.abs(asset.currentPercentage - asset.targetPercentage) >= threshold
  );
}

// Calculate rebalancing frequency
export function calculateOptimalFrequency(
  volatility: number,
  gasCost: number,
  portfolioValue: number
): 'daily' | 'weekly' | 'monthly' | 'quarterly' {
  const costPercentage = (gasCost / portfolioValue) * 100;

  if (volatility > 50 && costPercentage < 0.5) return 'daily';
  if (volatility > 30 && costPercentage < 1) return 'weekly';
  if (volatility > 15) return 'monthly';
  return 'quarterly';
}

// Time-based rebalancing
export function shouldRebalanceByTime(
  lastRebalance: Date,
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly'
): boolean {
  const now = new Date();
  const daysSinceRebalance = Math.floor(
    (now.getTime() - lastRebalance.getTime()) / (1000 * 60 * 60 * 24)
  );

  switch (frequency) {
    case 'daily':
      return daysSinceRebalance >= 1;
    case 'weekly':
      return daysSinceRebalance >= 7;
    case 'monthly':
      return daysSinceRebalance >= 30;
    case 'quarterly':
      return daysSinceRebalance >= 90;
  }
}

// Calculate tax implications
export function calculateTaxImpact(
  actions: RebalanceAction[],
  taxRate: number = 0.2
): number {
  const totalGains = actions
    .filter((a) => a.action === 'sell')
    .reduce((sum, a) => sum + a.amount * 0.2, 0); // Assuming 20% gain

  return totalGains * taxRate;
}

// Threshold-based rebalancing
export function calculateThresholdBands(
  targetPercentage: number,
  bandWidth: number = 5
): { lower: number; upper: number } {
  return {
    lower: targetPercentage - bandWidth,
    upper: targetPercentage + bandWidth,
  };
}

export default {
  calculateRebalance,
  needsRebalancing,
  calculateOptimalFrequency,
  shouldRebalanceByTime,
  calculateTaxImpact,
  calculateThresholdBands,
};
