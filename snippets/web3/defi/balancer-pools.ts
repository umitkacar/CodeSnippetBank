/**
 * Balancer Protocol Integration
 * Weighted pools and liquidity management
 */

import { BrowserProvider, Contract } from 'ethers';
import { useWriteContract, useWaitForTransactionReceipt } from 'wagmi';

const BALANCER_VAULT_ABI = [
  'function swap((bytes32 poolId, uint8 kind, address assetIn, address assetOut, uint256 amount, bytes userData) single, (address sender, bool fromInternalBalance, address recipient, bool toInternalBalance) funds, uint256 limit, uint256 deadline) external payable returns (uint256)',
  'function joinPool(bytes32 poolId, address sender, address recipient, (address[] assets, uint256[] maxAmountsIn, bytes userData, bool fromInternalBalance) request) external payable',
  'function exitPool(bytes32 poolId, address sender, address recipient, (address[] assets, uint256[] minAmountsOut, bytes userData, bool toInternalBalance) request) external',
  'function getPoolTokens(bytes32 poolId) external view returns (address[] tokens, uint256[] balances, uint256 lastChangeBlock)',
];

const BALANCER_VAULT = '0xBA12222222228d8Ba445958a75a0704d566BF2C8';

// Swap on Balancer
export function useBalancerSwap() {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const swap = async (
    poolId: string,
    assetIn: string,
    assetOut: string,
    amount: bigint,
    minAmountOut: bigint,
    sender: string,
    recipient: string,
    deadline: number
  ) => {
    const single = {
      poolId,
      kind: 0, // GIVEN_IN
      assetIn,
      assetOut,
      amount,
      userData: '0x',
    };

    const funds = {
      sender,
      fromInternalBalance: false,
      recipient,
      toInternalBalance: false,
    };

    writeContract({
      address: BALANCER_VAULT as `0x${string}`,
      abi: BALANCER_VAULT_ABI,
      functionName: 'swap',
      args: [single, funds, minAmountOut, deadline],
    });
  };

  return {
    swap,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Join Balancer pool
export function useBalancerJoinPool() {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const joinPool = async (
    poolId: string,
    sender: string,
    recipient: string,
    assets: string[],
    maxAmountsIn: bigint[]
  ) => {
    const request = {
      assets,
      maxAmountsIn,
      userData: '0x',
      fromInternalBalance: false,
    };

    writeContract({
      address: BALANCER_VAULT as `0x${string}`,
      abi: BALANCER_VAULT_ABI,
      functionName: 'joinPool',
      args: [poolId, sender, recipient, request],
    });
  };

  return {
    joinPool,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Exit Balancer pool
export function useBalancerExitPool() {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const exitPool = async (
    poolId: string,
    sender: string,
    recipient: string,
    assets: string[],
    minAmountsOut: bigint[]
  ) => {
    const request = {
      assets,
      minAmountsOut,
      userData: '0x',
      toInternalBalance: false,
    };

    writeContract({
      address: BALANCER_VAULT as `0x${string}`,
      abi: BALANCER_VAULT_ABI,
      functionName: 'exitPool',
      args: [poolId, sender, recipient, request],
    });
  };

  return {
    exitPool,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Get pool tokens and balances
export async function getBalancerPoolTokens(
  provider: BrowserProvider,
  poolId: string
): Promise<{ tokens: string[]; balances: bigint[] }> {
  const vault = new Contract(BALANCER_VAULT, BALANCER_VAULT_ABI, provider);
  const result = await vault.getPoolTokens(poolId);

  return {
    tokens: result[0],
    balances: result[1],
  };
}

export default {
  useBalancerSwap,
  useBalancerJoinPool,
  useBalancerExitPool,
  getBalancerPoolTokens,
  BALANCER_VAULT,
};
