/**
 * Lending Aggregator
 * Find best lending rates across protocols
 */

import { BrowserProvider } from 'ethers';

export interface LendingRate {
  protocol: string;
  supplyAPY: number;
  borrowAPY: number;
  asset: string;
}

// Get Aave rates
export async function getAaveRates(
  provider: BrowserProvider,
  asset: string
): Promise<LendingRate> {
  // Simplified - would query Aave contracts
  return {
    protocol: 'Aave',
    supplyAPY: 2.5,
    borrowAPY: 3.5,
    asset,
  };
}

// Get Compound rates
export async function getCompoundRates(
  provider: BrowserProvider,
  asset: string
): Promise<LendingRate> {
  return {
    protocol: 'Compound',
    supplyAPY: 2.3,
    borrowAPY: 3.7,
    asset,
  };
}

// Compare all lending protocols
export async function compareLendingRates(
  provider: BrowserProvider,
  asset: string
): Promise<LendingRate[]> {
  const [aaveRates, compoundRates] = await Promise.all([
    getAaveRates(provider, asset),
    getCompoundRates(provider, asset),
  ]);

  return [aaveRates, compoundRates].sort(
    (a, b) => b.supplyAPY - a.supplyAPY
  );
}

// Find best supply rate
export function findBestSupplyRate(rates: LendingRate[]): LendingRate {
  return rates.reduce((best, current) =>
    current.supplyAPY > best.supplyAPY ? current : best
  );
}

// Find best borrow rate
export function findBestBorrowRate(rates: LendingRate[]): LendingRate {
  return rates.reduce((best, current) =>
    current.borrowAPY < best.borrowAPY ? current : best
  );
}

// Calculate potential earnings
export function calculateYearlyEarnings(
  principal: number,
  apy: number
): number {
  return principal * (apy / 100);
}

export default {
  getAaveRates,
  getCompoundRates,
  compareLendingRates,
  findBestSupplyRate,
  findBestBorrowRate,
  calculateYearlyEarnings,
};
