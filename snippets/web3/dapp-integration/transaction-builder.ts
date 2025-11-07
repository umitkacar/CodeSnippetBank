/**
 * Transaction Builder
 * Build and encode complex transactions
 */

import { BrowserProvider, Contract, AbiCoder, keccak256, toUtf8Bytes } from 'ethers';

// Encode function call
export function encodeFunctionCall(
  abi: any[],
  functionName: string,
  args: any[]
): string {
  const iface = new (require('ethers')).Interface(abi);
  return iface.encodeFunctionData(functionName, args);
}

// Decode function call
export function decodeFunctionCall(abi: any[], data: string): any {
  const iface = new (require('ethers')).Interface(abi);
  return iface.parseTransaction({ data });
}

// Build transaction object
export interface TransactionRequest {
  to: string;
  data: string;
  value?: bigint;
  gasLimit?: bigint;
  maxFeePerGas?: bigint;
  maxPriorityFeePerGas?: bigint;
}

export function buildTransaction(
  contractAddress: string,
  abi: any[],
  functionName: string,
  args: any[],
  value?: bigint
): TransactionRequest {
  const data = encodeFunctionCall(abi, functionName, args);

  return {
    to: contractAddress,
    data,
    value: value || 0n,
  };
}

// Estimate gas for transaction
export async function estimateTransactionGas(
  provider: BrowserProvider,
  tx: TransactionRequest
): Promise<bigint> {
  return await provider.estimateGas(tx);
}

// Sign transaction
export async function signTransaction(
  provider: BrowserProvider,
  tx: TransactionRequest
): Promise<string> {
  const signer = await provider.getSigner();
  return await signer.signTransaction(tx);
}

// Get function selector
export function getFunctionSelector(functionSignature: string): string {
  return keccak256(toUtf8Bytes(functionSignature)).slice(0, 10);
}

// Encode constructor arguments
export function encodeConstructorArgs(types: string[], values: any[]): string {
  const abiCoder = AbiCoder.defaultAbiCoder();
  return abiCoder.encode(types, values);
}

// Batch transaction builder
export function buildBatchTransactions(
  calls: Array<{
    address: string;
    abi: any[];
    functionName: string;
    args: any[];
    value?: bigint;
  }>
): TransactionRequest[] {
  return calls.map((call) =>
    buildTransaction(call.address, call.abi, call.functionName, call.args, call.value)
  );
}

export default {
  encodeFunctionCall,
  decodeFunctionCall,
  buildTransaction,
  estimateTransactionGas,
  signTransaction,
  getFunctionSelector,
  encodeConstructorArgs,
  buildBatchTransactions,
};
