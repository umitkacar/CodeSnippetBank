/**
 * Yield Aggregator (Yearn-style)
 * Auto-compound yield strategies
 */

import { BrowserProvider, Contract } from 'ethers';
import { useWriteContract, useWaitForTransactionReceipt, useReadContract } from 'wagmi';

const VAULT_ABI = [
  'function deposit(uint256 amount) external returns (uint256)',
  'function withdraw(uint256 shares) external returns (uint256)',
  'function pricePerShare() external view returns (uint256)',
  'function totalAssets() external view returns (uint256)',
  'function balanceOf(address account) external view returns (uint256)',
];

// Deposit into vault
export function useVaultDeposit(vaultAddress: string) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const deposit = async (amount: bigint) => {
    writeContract({
      address: vaultAddress as `0x${string}`,
      abi: VAULT_ABI,
      functionName: 'deposit',
      args: [amount],
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

// Withdraw from vault
export function useVaultWithdraw(vaultAddress: string) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const withdraw = async (shares: bigint) => {
    writeContract({
      address: vaultAddress as `0x${string}`,
      abi: VAULT_ABI,
      functionName: 'withdraw',
      args: [shares],
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

// Get price per share
export function usePricePerShare(vaultAddress: string) {
  const { data, isLoading, refetch } = useReadContract({
    address: vaultAddress as `0x${string}`,
    abi: VAULT_ABI,
    functionName: 'pricePerShare',
  });

  return {
    pricePerShare: data as bigint,
    isLoading,
    refetch,
  };
}

// Calculate vault APY
export async function calculateVaultAPY(
  provider: BrowserProvider,
  vaultAddress: string,
  initialPricePerShare: bigint,
  daysPassed: number
): Promise<number> {
  const vault = new Contract(vaultAddress, VAULT_ABI, provider);
  const currentPricePerShare = await vault.pricePerShare();

  const growth =
    Number(currentPricePerShare - initialPricePerShare) /
    Number(initialPricePerShare);

  const apy = (growth * 365) / daysPassed * 100;

  return apy;
}

// Get user vault balance
export async function getUserVaultBalance(
  provider: BrowserProvider,
  vaultAddress: string,
  userAddress: string
): Promise<{ shares: bigint; underlyingValue: bigint }> {
  const vault = new Contract(vaultAddress, VAULT_ABI, provider);

  const [shares, pricePerShare] = await Promise.all([
    vault.balanceOf(userAddress),
    vault.pricePerShare(),
  ]);

  const underlyingValue = (shares * pricePerShare) / BigInt(1e18);

  return { shares, underlyingValue };
}

export default {
  useVaultDeposit,
  useVaultWithdraw,
  usePricePerShare,
  calculateVaultAPY,
  getUserVaultBalance,
};
