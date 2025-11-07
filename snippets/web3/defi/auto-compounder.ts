/**
 * Auto-Compounder
 * Automatic reward harvesting and reinvestment
 */

import { BrowserProvider, Contract } from 'ethers';

const AUTO_COMPOUND_ABI = [
  'function compound() external',
  'function deposit(uint256 amount) external',
  'function withdraw(uint256 shares) external',
  'function balanceOf(address account) external view returns (uint256)',
  'function totalSupply() external view returns (uint256)',
  'function getPricePerFullShare() external view returns (uint256)',
];

// Deposit and start auto-compounding
export async function depositAutoCompound(
  provider: BrowserProvider,
  vaultAddress: string,
  amount: bigint
): Promise<any> {
  const signer = await provider.getSigner();
  const vault = new Contract(vaultAddress, AUTO_COMPOUND_ABI, signer);

  const tx = await vault.deposit(amount);
  return await tx.wait();
}

// Manually trigger compound
export async function triggerCompound(
  provider: BrowserProvider,
  vaultAddress: string
): Promise<any> {
  const signer = await provider.getSigner();
  const vault = new Contract(vaultAddress, AUTO_COMPOUND_ABI, signer);

  const tx = await vault.compound();
  return await tx.wait();
}

// Calculate compound frequency impact
export function calculateCompoundEffect(
  principal: number,
  apy: number,
  compounds: number,
  days: number
): { simple: number; compound: number; difference: number } {
  const years = days / 365;

  // Simple interest
  const simple = principal * (1 + (apy / 100) * years);

  // Compound interest
  const periodsPerYear = compounds;
  const periods = years * periodsPerYear;
  const ratePerPeriod = apy / 100 / periodsPerYear;
  const compound = principal * Math.pow(1 + ratePerPeriod, periods);

  const difference = compound - simple;

  return {
    simple,
    compound,
    difference,
  };
}

// Optimal compound frequency calculator
export function calculateOptimalCompoundFrequency(
  apy: number,
  gasCost: number,
  principal: number
): number {
  const targetGainPerCompound = gasCost * 2; // Want 2x gas cost as minimum gain

  const dailyRate = apy / 100 / 365;
  const daysNeeded = targetGainPerCompound / (principal * dailyRate);

  return Math.max(1, Math.ceil(daysNeeded));
}

export default {
  depositAutoCompound,
  triggerCompound,
  calculateCompoundEffect,
  calculateOptimalCompoundFrequency,
};
