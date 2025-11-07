/**
 * Batch Transactions
 * Execute multiple transactions in sequence or parallel
 */

import { BrowserProvider, Contract } from 'ethers';
import { useWriteContract, useWaitForTransactionReceipt } from 'wagmi';
import { useState } from 'react';

// Sequential transaction execution
export async function executeSequentialTransactions(
  provider: BrowserProvider,
  calls: Array<{
    address: string;
    abi: any[];
    functionName: string;
    args: any[];
    value?: bigint;
  }>
): Promise<any[]> {
  const signer = await provider.getSigner();
  const receipts = [];

  for (const call of calls) {
    const contract = new Contract(call.address, call.abi, signer);
    const tx = await contract[call.functionName](...call.args, {
      value: call.value || 0n,
    });
    const receipt = await tx.wait();
    receipts.push(receipt);
  }

  return receipts;
}

// Batch transaction hook
export function useBatchTransactions() {
  const [isExecuting, setIsExecuting] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [receipts, setReceipts] = useState<any[]>([]);
  const [error, setError] = useState<Error | null>(null);

  const execute = async (
    provider: BrowserProvider,
    calls: Array<{
      address: string;
      abi: any[];
      functionName: string;
      args: any[];
      value?: bigint;
    }>
  ) => {
    setIsExecuting(true);
    setCurrentStep(0);
    setReceipts([]);
    setError(null);

    try {
      const signer = await provider.getSigner();

      for (let i = 0; i < calls.length; i++) {
        setCurrentStep(i + 1);
        const call = calls[i];
        const contract = new Contract(call.address, call.abi, signer);
        const tx = await contract[call.functionName](...call.args, {
          value: call.value || 0n,
        });
        const receipt = await tx.wait();
        setReceipts((prev) => [...prev, receipt]);
      }
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setIsExecuting(false);
    }
  };

  return {
    execute,
    isExecuting,
    currentStep,
    receipts,
    error,
  };
}

// Multicall contract integration
const MULTICALL_ABI = [
  'function aggregate(tuple(address target, bytes callData)[] calls) returns (uint256 blockNumber, bytes[] returnData)',
];

export async function executeMulticall(
  provider: BrowserProvider,
  multicallAddress: string,
  calls: Array<{ target: string; callData: string }>
): Promise<any> {
  const signer = await provider.getSigner();
  const multicall = new Contract(multicallAddress, MULTICALL_ABI, signer);

  const tx = await multicall.aggregate(calls);
  return await tx.wait();
}

// Approve and execute pattern
export async function approveAndExecute(
  provider: BrowserProvider,
  tokenAddress: string,
  spenderAddress: string,
  amount: bigint,
  executeCallback: () => Promise<any>
): Promise<{ approveReceipt: any; executeReceipt: any }> {
  const signer = await provider.getSigner();

  // Approve
  const tokenAbi = ['function approve(address spender, uint256 amount) returns (bool)'];
  const token = new Contract(tokenAddress, tokenAbi, signer);
  const approveTx = await token.approve(spenderAddress, amount);
  const approveReceipt = await approveTx.wait();

  // Execute
  const executeReceipt = await executeCallback();

  return { approveReceipt, executeReceipt };
}

export default {
  executeSequentialTransactions,
  useBatchTransactions,
  executeMulticall,
  approveAndExecute,
};
