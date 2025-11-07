/**
 * Yield Farming Utilities
 * Stake LP tokens and earn rewards
 */

import { BrowserProvider, Contract } from 'ethers';
import { useWriteContract, useWaitForTransactionReceipt, useReadContract } from 'wagmi';

const MASTERCHEF_ABI = [
  'function deposit(uint256 pid, uint256 amount) external',
  'function withdraw(uint256 pid, uint256 amount) external',
  'function emergencyWithdraw(uint256 pid) external',
  'function pendingReward(uint256 pid, address user) external view returns (uint256)',
  'function userInfo(uint256 pid, address user) external view returns (uint256 amount, uint256 rewardDebt)',
  'function poolInfo(uint256 pid) external view returns (address lpToken, uint256 allocPoint, uint256 lastRewardBlock, uint256 accRewardPerShare)',
];

// Stake LP tokens
export function useYieldFarmDeposit(masterChefAddress: string) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const deposit = async (poolId: number, amount: bigint) => {
    writeContract({
      address: masterChefAddress as `0x${string}`,
      abi: MASTERCHEF_ABI,
      functionName: 'deposit',
      args: [BigInt(poolId), amount],
    });
  };

  return {
    deposit,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Unstake LP tokens
export function useYieldFarmWithdraw(masterChefAddress: string) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const withdraw = async (poolId: number, amount: bigint) => {
    writeContract({
      address: masterChefAddress as `0x${string}`,
      abi: MASTERCHEF_ABI,
      functionName: 'withdraw',
      args: [BigInt(poolId), amount],
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

// Get pending rewards
export function usePendingRewards(
  masterChefAddress: string,
  poolId: number,
  userAddress: string
) {
  const { data, isLoading, refetch } = useReadContract({
    address: masterChefAddress as `0x${string}`,
    abi: MASTERCHEF_ABI,
    functionName: 'pendingReward',
    args: [BigInt(poolId), userAddress],
  });

  return {
    pending: data as bigint,
    isLoading,
    refetch,
  };
}

// Get user staked amount
export function useUserStakeInfo(
  masterChefAddress: string,
  poolId: number,
  userAddress: string
) {
  const { data, isLoading, refetch } = useReadContract({
    address: masterChefAddress as `0x${string}`,
    abi: MASTERCHEF_ABI,
    functionName: 'userInfo',
    args: [BigInt(poolId), userAddress],
  });

  return {
    amount: data ? (data as any)[0] : 0n,
    rewardDebt: data ? (data as any)[1] : 0n,
    isLoading,
    refetch,
  };
}

// Get pool info
export async function getPoolInfo(
  provider: BrowserProvider,
  masterChefAddress: string,
  poolId: number
): Promise<{
  lpToken: string;
  allocPoint: bigint;
  lastRewardBlock: bigint;
  accRewardPerShare: bigint;
}> {
  const masterChef = new Contract(masterChefAddress, MASTERCHEF_ABI, provider);
  const info = await masterChef.poolInfo(poolId);

  return {
    lpToken: info[0],
    allocPoint: info[1],
    lastRewardBlock: info[2],
    accRewardPerShare: info[3],
  };
}

// Calculate APR
export async function calculateFarmAPR(
  rewardPerBlock: bigint,
  rewardTokenPrice: number,
  totalStaked: bigint,
  lpTokenPrice: number,
  allocPoint: bigint,
  totalAllocPoint: bigint
): Promise<number> {
  const blocksPerYear = 2_102_400n; // ~15s per block
  const poolRewardPerYear =
    (rewardPerBlock * blocksPerYear * allocPoint) / totalAllocPoint;

  const yearlyRewardValue = Number(poolRewardPerYear) * rewardTokenPrice;
  const stakedValue = Number(totalStaked) * lpTokenPrice;

  return stakedValue > 0 ? (yearlyRewardValue / stakedValue) * 100 : 0;
}

// Harvest rewards (withdraw 0)
export async function harvestRewards(
  provider: BrowserProvider,
  masterChefAddress: string,
  poolId: number
): Promise<any> {
  const signer = await provider.getSigner();
  const masterChef = new Contract(masterChefAddress, MASTERCHEF_ABI, signer);

  const tx = await masterChef.withdraw(poolId, 0);
  return await tx.wait();
}

export default {
  useYieldFarmDeposit,
  useYieldFarmWithdraw,
  usePendingRewards,
  useUserStakeInfo,
  getPoolInfo,
  calculateFarmAPR,
  harvestRewards,
};
