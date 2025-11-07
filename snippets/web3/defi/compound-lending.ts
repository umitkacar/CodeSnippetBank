/**
 * Compound V3 Protocol
 * Supply and borrow assets on Compound
 */

import { BrowserProvider, Contract } from 'ethers';
import { useWriteContract, useWaitForTransactionReceipt } from 'wagmi';

const COMPOUND_COMET_ABI = [
  'function supply(address asset, uint amount) external',
  'function withdraw(address asset, uint amount) external',
  'function borrow(uint amount) external',
  'function repay(uint amount) external',
  'function collateralBalanceOf(address account, address asset) external view returns (uint128)',
  'function borrowBalanceOf(address account) external view returns (uint256)',
];

// Compound V3 USDC market on Ethereum
const COMPOUND_USDC_COMET = '0xc3d688B66703497DAA19211EEdff47f25384cdc3';

// Supply collateral
export function useCompoundSupply(cometAddress: string = COMPOUND_USDC_COMET) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const supply = async (asset: string, amount: bigint) => {
    writeContract({
      address: cometAddress as `0x${string}`,
      abi: COMPOUND_COMET_ABI,
      functionName: 'supply',
      args: [asset, amount],
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

// Withdraw collateral
export function useCompoundWithdraw(cometAddress: string = COMPOUND_USDC_COMET) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const withdraw = async (asset: string, amount: bigint) => {
    writeContract({
      address: cometAddress as `0x${string}`,
      abi: COMPOUND_COMET_ABI,
      functionName: 'withdraw',
      args: [asset, amount],
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

// Borrow base asset (e.g., USDC)
export function useCompoundBorrow(cometAddress: string = COMPOUND_USDC_COMET) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const borrow = async (amount: bigint) => {
    writeContract({
      address: cometAddress as `0x${string}`,
      abi: COMPOUND_COMET_ABI,
      functionName: 'borrow',
      args: [amount],
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

// Repay borrowed amount
export function useCompoundRepay(cometAddress: string = COMPOUND_USDC_COMET) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const repay = async (amount: bigint) => {
    writeContract({
      address: cometAddress as `0x${string}`,
      abi: COMPOUND_COMET_ABI,
      functionName: 'repay',
      args: [amount],
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

// Get collateral balance
export async function getCompoundCollateralBalance(
  provider: BrowserProvider,
  cometAddress: string,
  account: string,
  asset: string
): Promise<bigint> {
  const comet = new Contract(cometAddress, COMPOUND_COMET_ABI, provider);
  return await comet.collateralBalanceOf(account, asset);
}

// Get borrow balance
export async function getCompoundBorrowBalance(
  provider: BrowserProvider,
  cometAddress: string,
  account: string
): Promise<bigint> {
  const comet = new Contract(cometAddress, COMPOUND_COMET_ABI, provider);
  return await comet.borrowBalanceOf(account);
}

export default {
  useCompoundSupply,
  useCompoundWithdraw,
  useCompoundBorrow,
  useCompoundRepay,
  getCompoundCollateralBalance,
  getCompoundBorrowBalance,
  COMPOUND_USDC_COMET,
};
