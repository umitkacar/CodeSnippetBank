/**
 * Aave V3 Lending Protocol
 * Supply, borrow, and repay on Aave
 */

import { BrowserProvider, Contract } from 'ethers';
import { useWriteContract, useWaitForTransactionReceipt, useReadContract } from 'wagmi';

const AAVE_POOL_ABI = [
  'function supply(address asset, uint256 amount, address onBehalfOf, uint16 referralCode) external',
  'function withdraw(address asset, uint256 amount, address to) external returns (uint256)',
  'function borrow(address asset, uint256 amount, uint256 interestRateMode, uint16 referralCode, address onBehalfOf) external',
  'function repay(address asset, uint256 amount, uint256 interestRateMode, address onBehalfOf) external returns (uint256)',
  'function getUserAccountData(address user) external view returns (uint256 totalCollateralBase, uint256 totalDebtBase, uint256 availableBorrowsBase, uint256 currentLiquidationThreshold, uint256 ltv, uint256 healthFactor)',
];

const AAVE_V3_POOL = '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2'; // Ethereum mainnet

export enum InterestRateMode {
  STABLE = 1,
  VARIABLE = 2,
}

// Supply assets to Aave
export function useAaveSupply() {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const supply = async (asset: string, amount: bigint, onBehalfOf: string) => {
    writeContract({
      address: AAVE_V3_POOL as `0x${string}`,
      abi: AAVE_POOL_ABI,
      functionName: 'supply',
      args: [asset, amount, onBehalfOf, 0],
    });
  };

  return {
    supply,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Withdraw from Aave
export function useAaveWithdraw() {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const withdraw = async (asset: string, amount: bigint, to: string) => {
    writeContract({
      address: AAVE_V3_POOL as `0x${string}`,
      abi: AAVE_POOL_ABI,
      functionName: 'withdraw',
      args: [asset, amount, to],
    });
  };

  return {
    withdraw,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Borrow from Aave
export function useAaveBorrow() {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const borrow = async (
    asset: string,
    amount: bigint,
    interestRateMode: InterestRateMode,
    onBehalfOf: string
  ) => {
    writeContract({
      address: AAVE_V3_POOL as `0x${string}`,
      abi: AAVE_POOL_ABI,
      functionName: 'borrow',
      args: [asset, amount, interestRateMode, 0, onBehalfOf],
    });
  };

  return {
    borrow,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Repay borrowed assets
export function useAaveRepay() {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const repay = async (
    asset: string,
    amount: bigint,
    interestRateMode: InterestRateMode,
    onBehalfOf: string
  ) => {
    writeContract({
      address: AAVE_V3_POOL as `0x${string}`,
      abi: AAVE_POOL_ABI,
      functionName: 'repay',
      args: [asset, amount, interestRateMode, onBehalfOf],
    });
  };

  return {
    repay,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Get user account data
export async function getAaveAccountData(
  provider: BrowserProvider,
  userAddress: string
): Promise<{
  totalCollateral: bigint;
  totalDebt: bigint;
  availableBorrows: bigint;
  liquidationThreshold: bigint;
  ltv: bigint;
  healthFactor: bigint;
}> {
  const pool = new Contract(AAVE_V3_POOL, AAVE_POOL_ABI, provider);

  const data = await pool.getUserAccountData(userAddress);

  return {
    totalCollateral: data[0],
    totalDebt: data[1],
    availableBorrows: data[2],
    liquidationThreshold: data[3],
    ltv: data[4],
    healthFactor: data[5],
  };
}

// Calculate health factor
export function isHealthy(healthFactor: bigint): boolean {
  return healthFactor > 1e18; // Health factor above 1.0
}

// Calculate max borrow amount
export function calculateMaxBorrow(
  totalCollateral: bigint,
  ltv: bigint,
  currentDebt: bigint
): bigint {
  const maxDebt = (totalCollateral * ltv) / 10000n;
  return maxDebt > currentDebt ? maxDebt - currentDebt : 0n;
}

export default {
  useAaveSupply,
  useAaveWithdraw,
  useAaveBorrow,
  useAaveRepay,
  getAaveAccountData,
  isHealthy,
  calculateMaxBorrow,
  InterestRateMode,
  AAVE_V3_POOL,
};
