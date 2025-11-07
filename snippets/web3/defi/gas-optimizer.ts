/**
 * DeFi Gas Optimizer
 * Optimize gas usage for DeFi transactions
 */

import { BrowserProvider } from 'ethers';

export interface GasOptimization {
  usePermit: boolean;
  batchTransactions: boolean;
  useFlashLoan: boolean;
  optimalTime: string;
}

// Get current gas price in gwei
export async function getCurrentGasPrice(
  provider: BrowserProvider
): Promise<{ gasPrice: bigint; gwei: number }> {
  const feeData = await provider.getFeeData();
  const gasPrice = feeData.gasPrice || 0n;

  return {
    gasPrice,
    gwei: Number(gasPrice) / 1e9,
  };
}

// Calculate transaction cost
export async function calculateTxCost(
  provider: BrowserProvider,
  gasLimit: number
): Promise<{ costWei: bigint; costEth: string; costUSD: number }> {
  const { gasPrice } = await getCurrentGasPrice(provider);
  const costWei = gasPrice * BigInt(gasLimit);
  const costEth = Number(costWei) / 1e18;

  // Assuming ETH price (would fetch from oracle)
  const ethPrice = 2000;
  const costUSD = costEth * ethPrice;

  return {
    costWei,
    costEth: costEth.toFixed(6),
    costUSD,
  };
}

// Recommend gas optimization strategies
export function recommendOptimizations(
  txCost: number,
  swapAmount: number
): GasOptimization {
  return {
    usePermit: txCost > 5, // Use permit if gas > $5
    batchTransactions: txCost > 20, // Batch if gas > $20
    useFlashLoan: swapAmount > 10000, // Flash loan for large amounts
    optimalTime: getOptimalGasTime(),
  };
}

// Get optimal time for low gas
function getOptimalGasTime(): string {
  const hour = new Date().getUTCHours();

  // Weekends are generally cheaper
  const day = new Date().getUTCDay();
  if (day === 0 || day === 6) {
    return 'Weekends typically have lower gas prices';
  }

  // Off-peak hours
  if (hour >= 0 && hour < 8) {
    return 'Current time is good - off-peak hours';
  }

  if (hour >= 8 && hour < 16) {
    return 'Peak hours - wait for off-peak if not urgent';
  }

  return 'Moderate gas time';
}

// Calculate savings from permit
export function calculatePermitSavings(approveGas: number, permitGas: number = 0): number {
  const gasSaved = approveGas;
  return gasSaved;
}

// Should use multicall
export function shouldUseMulticall(
  numberOfCalls: number,
  individualGas: number,
  multicallOverhead: number = 21000
): boolean {
  const individualTotal = numberOfCalls * individualGas;
  const multicallTotal = multicallOverhead + numberOfCalls * (individualGas * 0.8);

  return multicallTotal < individualTotal;
}

// Estimate flash loan profitability
export function isFlashLoanProfitable(
  profit: bigint,
  gasPrice: bigint,
  gasLimit: number = 500000
): boolean {
  const gasCost = gasPrice * BigInt(gasLimit);
  return profit > gasCost * 2n; // Need 2x gas cost to be worthwhile
}

export default {
  getCurrentGasPrice,
  calculateTxCost,
  recommendOptimizations,
  calculatePermitSavings,
  shouldUseMulticall,
  isFlashLoanProfitable,
};
