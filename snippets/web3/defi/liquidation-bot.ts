/**
 * Liquidation Bot
 * Monitor and execute liquidations
 */

import { BrowserProvider, Contract } from 'ethers';

const LENDING_POOL_ABI = [
  'function liquidationCall(address collateral, address debt, address user, uint256 debtToCover, bool receiveAToken) external',
  'function getUserAccountData(address user) external view returns (uint256 totalCollateral, uint256 totalDebt, uint256 availableBorrows, uint256 currentLiquidationThreshold, uint256 ltv, uint256 healthFactor)',
];

export interface LiquidationCandidate {
  user: string;
  healthFactor: bigint;
  totalCollateral: bigint;
  totalDebt: bigint;
  profitEstimate: bigint;
}

// Check if user is liquidatable
export async function isLiquidatable(
  provider: BrowserProvider,
  lendingPoolAddress: string,
  userAddress: string
): Promise<boolean> {
  const pool = new Contract(lendingPoolAddress, LENDING_POOL_ABI, provider);
  const data = await pool.getUserAccountData(userAddress);

  const healthFactor = data[5];
  return healthFactor < BigInt(1e18); // Health factor < 1.0
}

// Execute liquidation
export async function executeLiquidation(
  provider: BrowserProvider,
  lendingPoolAddress: string,
  collateralAsset: string,
  debtAsset: string,
  user: string,
  debtToCover: bigint
): Promise<any> {
  const signer = await provider.getSigner();
  const pool = new Contract(lendingPoolAddress, LENDING_POOL_ABI, signer);

  const tx = await pool.liquidationCall(
    collateralAsset,
    debtAsset,
    user,
    debtToCover,
    false
  );

  return await tx.wait();
}

// Calculate liquidation profit
export function calculateLiquidationProfit(
  debtAmount: bigint,
  collateralAmount: bigint,
  liquidationBonus: number, // e.g., 5% = 5
  gasPrice: bigint,
  gasUsed: number
): bigint {
  const bonus = (collateralAmount * BigInt(liquidationBonus)) / 100n;
  const gasCost = gasPrice * BigInt(gasUsed);

  return bonus - gasCost;
}

// Monitor health factors
export async function monitorHealthFactors(
  provider: BrowserProvider,
  lendingPoolAddress: string,
  users: string[]
): Promise<LiquidationCandidate[]> {
  const pool = new Contract(lendingPoolAddress, LENDING_POOL_ABI, provider);

  const candidates: LiquidationCandidate[] = [];

  for (const user of users) {
    try {
      const data = await pool.getUserAccountData(user);
      const healthFactor = data[5];

      if (healthFactor < BigInt(1.1e18)) {
        // Close to liquidation
        candidates.push({
          user,
          healthFactor,
          totalCollateral: data[0],
          totalDebt: data[1],
          profitEstimate: 0n, // Would calculate actual profit
        });
      }
    } catch (error) {
      console.error(`Error checking user ${user}:`, error);
    }
  }

  return candidates.sort((a, b) =>
    Number(a.healthFactor - b.healthFactor)
  );
}

export default {
  isLiquidatable,
  executeLiquidation,
  calculateLiquidationProfit,
  monitorHealthFactors,
};
