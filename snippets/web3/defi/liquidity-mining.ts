/**
 * Liquidity Mining
 * Provide liquidity and earn rewards
 */

import { BrowserProvider, Contract } from 'ethers';
import { useWriteContract, useWaitForTransactionReceipt, useReadContract } from 'wagmi';

const LIQUIDITY_MINING_ABI = [
  'function stake(uint256 poolId, uint256 amount) external',
  'function unstake(uint256 poolId, uint256 amount) external',
  'function harvest(uint256 poolId) external',
  'function pendingRewards(uint256 poolId, address user) external view returns (uint256)',
  'function userInfo(uint256 poolId, address user) external view returns (uint256 amount, uint256 rewardDebt)',
  'function poolInfo(uint256 poolId) external view returns (address lpToken, uint256 allocPoint, uint256 lastRewardTime, uint256 accRewardPerShare, uint256 depositFee)',
];

// Stake LP tokens for mining
export function useLiquidityMining(miningAddress: string) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const stake = async (poolId: number, amount: bigint) => {
    writeContract({
      address: miningAddress as `0x${string}`,
      abi: LIQUIDITY_MINING_ABI,
      functionName: 'stake',
      args: [BigInt(poolId), amount],
    });
  };

  const unstake = async (poolId: number, amount: bigint) => {
    writeContract({
      address: miningAddress as `0x${string}`,
      abi: LIQUIDITY_MINING_ABI,
      functionName: 'unstake',
      args: [BigInt(poolId), amount],
    });
  };

  const harvest = async (poolId: number) => {
    writeContract({
      address: miningAddress as `0x${string}`,
      abi: LIQUIDITY_MINING_ABI,
      functionName: 'harvest',
      args: [BigInt(poolId)],
    });
  };

  return {
    stake,
    unstake,
    harvest,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Get pending rewards
export function usePendingMiningRewards(
  miningAddress: string,
  poolId: number,
  userAddress: string
) {
  const { data, isLoading, refetch } = useReadContract({
    address: miningAddress as `0x${string}`,
    abi: LIQUIDITY_MINING_ABI,
    functionName: 'pendingRewards',
    args: [BigInt(poolId), userAddress],
  });

  return {
    rewards: data as bigint,
    isLoading,
    refetch,
  };
}

// Calculate mining APR
export async function calculateMiningAPR(
  rewardPerSecond: bigint,
  rewardTokenPrice: number,
  totalStaked: bigint,
  lpTokenPrice: number,
  allocPoint: bigint,
  totalAllocPoint: bigint
): Promise<number> {
  const SECONDS_PER_YEAR = 31536000n;

  const poolRewardPerYear =
    (rewardPerSecond * SECONDS_PER_YEAR * allocPoint) / totalAllocPoint;

  const yearlyRewardValue = Number(poolRewardPerYear) * rewardTokenPrice;
  const totalStakedValue = Number(totalStaked) * lpTokenPrice;

  return totalStakedValue > 0 ? (yearlyRewardValue / totalStakedValue) * 100 : 0;
}

// Calculate impermanent loss
export function calculateImpermanentLoss(
  priceRatio: number
): { loss: number; percentage: number } {
  const k = priceRatio;
  const loss = (2 * Math.sqrt(k)) / (1 + k) - 1;
  const percentage = loss * 100;

  return { loss, percentage };
}

export default {
  useLiquidityMining,
  usePendingMiningRewards,
  calculateMiningAPR,
  calculateImpermanentLoss,
};
