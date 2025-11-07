/**
 * Staking Pools
 * Single-asset staking with rewards
 */

import { BrowserProvider, Contract } from 'ethers';
import { useWriteContract, useWaitForTransactionReceipt, useReadContract } from 'wagmi';

const STAKING_POOL_ABI = [
  'function stake(uint256 amount) external',
  'function withdraw(uint256 amount) external',
  'function getReward() external',
  'function exit() external',
  'function balanceOf(address account) external view returns (uint256)',
  'function earned(address account) external view returns (uint256)',
  'function rewardRate() external view returns (uint256)',
  'function totalSupply() external view returns (uint256)',
];

// Stake tokens
export function useStaking(stakingPoolAddress: string) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const stake = async (amount: bigint) => {
    writeContract({
      address: stakingPoolAddress as `0x${string}`,
      abi: STAKING_POOL_ABI,
      functionName: 'stake',
      args: [amount],
    });
  };

  const withdraw = async (amount: bigint) => {
    writeContract({
      address: stakingPoolAddress as `0x${string}`,
      abi: STAKING_POOL_ABI,
      functionName: 'withdraw',
      args: [amount],
    });
  };

  const claimRewards = async () => {
    writeContract({
      address: stakingPoolAddress as `0x${string}`,
      abi: STAKING_POOL_ABI,
      functionName: 'getReward',
    });
  };

  const exit = async () => {
    writeContract({
      address: stakingPoolAddress as `0x${string}`,
      abi: STAKING_POOL_ABI,
      functionName: 'exit',
    });
  };

  return {
    stake,
    withdraw,
    claimRewards,
    exit,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Get staked balance
export function useStakedBalance(stakingPoolAddress: string, userAddress: string) {
  const { data, isLoading, refetch } = useReadContract({
    address: stakingPoolAddress as `0x${string}`,
    abi: STAKING_POOL_ABI,
    functionName: 'balanceOf',
    args: [userAddress],
  });

  return {
    balance: data as bigint,
    isLoading,
    refetch,
  };
}

// Get earned rewards
export function useEarnedRewards(stakingPoolAddress: string, userAddress: string) {
  const { data, isLoading, refetch } = useReadContract({
    address: stakingPoolAddress as `0x${string}`,
    abi: STAKING_POOL_ABI,
    functionName: 'earned',
    args: [userAddress],
  });

  return {
    earned: data as bigint,
    isLoading,
    refetch,
  };
}

// Get staking APY
export async function getStakingAPY(
  provider: BrowserProvider,
  stakingPoolAddress: string,
  rewardTokenPrice: number,
  stakingTokenPrice: number
): Promise<number> {
  const pool = new Contract(stakingPoolAddress, STAKING_POOL_ABI, provider);

  const [rewardRate, totalSupply] = await Promise.all([
    pool.rewardRate(),
    pool.totalSupply(),
  ]);

  const SECONDS_PER_YEAR = 31536000n;
  const yearlyRewards = rewardRate * SECONDS_PER_YEAR;

  const yearlyRewardValue = Number(yearlyRewards) * rewardTokenPrice;
  const totalStakedValue = Number(totalSupply) * stakingTokenPrice;

  return totalStakedValue > 0 ? (yearlyRewardValue / totalStakedValue) * 100 : 0;
}

// Auto-compound calculator
export function calculateAutoCompound(
  principal: number,
  apy: number,
  compounds: number,
  days: number
): number {
  const periods = (days / 365) * compounds;
  const rate = apy / 100 / compounds;

  return principal * Math.pow(1 + rate, periods);
}

export default {
  useStaking,
  useStakedBalance,
  useEarnedRewards,
  getStakingAPY,
  calculateAutoCompound,
};
