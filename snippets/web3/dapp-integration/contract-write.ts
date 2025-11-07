/**
 * Contract Write Operations
 * Execute transactions on smart contracts
 */

import { useWriteContract, useWaitForTransactionReceipt } from 'wagmi';
import { BrowserProvider, Contract } from 'ethers';
import { parseEther, parseUnits } from 'ethers';

// ERC20 ABI for write operations
const ERC20_ABI = [
  'function transfer(address to, uint256 amount) returns (bool)',
  'function approve(address spender, uint256 amount) returns (bool)',
  'function transferFrom(address from, address to, uint256 amount) returns (bool)',
];

// Hook for contract write operations
export function useContractWrite() {
  const { data: hash, writeContract, isPending, error } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  return {
    hash,
    writeContract,
    isPending,
    isConfirming,
    isSuccess,
    error,
  };
}

// Transfer ERC20 tokens
export function useTokenTransfer(tokenAddress: string) {
  const { writeContract, hash, isPending, isConfirming, isSuccess, error } =
    useContractWrite();

  const transfer = async (to: string, amount: string, decimals: number = 18) => {
    const amountBN = parseUnits(amount, decimals);

    writeContract({
      address: tokenAddress as `0x${string}`,
      abi: ERC20_ABI,
      functionName: 'transfer',
      args: [to, amountBN],
    });
  };

  return {
    transfer,
    hash,
    isPending,
    isConfirming,
    isSuccess,
    error,
  };
}

// Approve ERC20 spending
export function useTokenApprove(tokenAddress: string) {
  const { writeContract, hash, isPending, isConfirming, isSuccess, error } =
    useContractWrite();

  const approve = async (spender: string, amount: string, decimals: number = 18) => {
    const amountBN = parseUnits(amount, decimals);

    writeContract({
      address: tokenAddress as `0x${string}`,
      abi: ERC20_ABI,
      functionName: 'approve',
      args: [spender, amountBN],
    });
  };

  return {
    approve,
    hash,
    isPending,
    isConfirming,
    isSuccess,
    error,
  };
}

// Write contract with ethers.js
export async function writeContractWithEthers(
  provider: BrowserProvider,
  contractAddress: string,
  abi: any[],
  functionName: string,
  args: any[] = [],
  value?: string
) {
  const signer = await provider.getSigner();
  const contract = new Contract(contractAddress, abi, signer);

  const tx = await contract[functionName](...args, {
    value: value ? parseEther(value) : undefined,
  });

  return await tx.wait();
}

// Generic contract write hook
export function useGenericContractWrite(
  address: string,
  abi: any[],
  functionName: string
) {
  const { writeContract, hash, isPending, isConfirming, isSuccess, error } =
    useContractWrite();

  const execute = async (args: any[], value?: bigint) => {
    writeContract({
      address: address as `0x${string}`,
      abi,
      functionName,
      args,
      value,
    });
  };

  return {
    execute,
    hash,
    isPending,
    isConfirming,
    isSuccess,
    error,
  };
}

// Batch contract writes
export async function batchContractWrites(
  provider: BrowserProvider,
  calls: Array<{
    address: string;
    abi: any[];
    functionName: string;
    args: any[];
    value?: string;
  }>
) {
  const signer = await provider.getSigner();
  const receipts = [];

  for (const call of calls) {
    const contract = new Contract(call.address, call.abi, signer);
    const tx = await contract[call.functionName](...call.args, {
      value: call.value ? parseEther(call.value) : undefined,
    });
    const receipt = await tx.wait();
    receipts.push(receipt);
  }

  return receipts;
}

export default {
  useContractWrite,
  useTokenTransfer,
  useTokenApprove,
  writeContractWithEthers,
  useGenericContractWrite,
  batchContractWrites,
};
