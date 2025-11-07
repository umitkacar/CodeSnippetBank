/**
 * Gas Optimization Utilities
 * Estimate and optimize gas usage
 */

import { useEstimateGas, useGasPrice, useFeeData } from 'wagmi';
import { BrowserProvider, Contract, parseEther, formatEther } from 'ethers';

// Estimate gas for transaction
export function useGasEstimate(
  address: string,
  abi: any[],
  functionName: string,
  args: any[]
) {
  const { data: gasEstimate, isLoading, error } = useEstimateGas({
    address: address as `0x${string}`,
    abi,
    functionName,
    args,
  });

  return {
    gasEstimate,
    isLoading,
    error,
  };
}

// Get current gas price
export function useCurrentGasPrice() {
  const { data: gasPrice, isLoading } = useGasPrice();

  return {
    gasPrice,
    gasPriceGwei: gasPrice ? Number(gasPrice) / 1e9 : 0,
    isLoading,
  };
}

// Get EIP-1559 fee data
export function useEIP1559Fees() {
  const { data: feeData, isLoading } = useFeeData();

  return {
    maxFeePerGas: feeData?.maxFeePerGas,
    maxPriorityFeePerGas: feeData?.maxPriorityFeePerGas,
    gasPrice: feeData?.gasPrice,
    isLoading,
  };
}

// Estimate gas with ethers.js
export async function estimateGasWithEthers(
  provider: BrowserProvider,
  contractAddress: string,
  abi: any[],
  functionName: string,
  args: any[] = [],
  value?: string
): Promise<bigint> {
  const contract = new Contract(contractAddress, abi, provider);

  return await contract[functionName].estimateGas(...args, {
    value: value ? parseEther(value) : undefined,
  });
}

// Calculate transaction cost
export async function calculateTransactionCost(
  provider: BrowserProvider,
  gasLimit: bigint
): Promise<{ cost: string; costEth: string }> {
  const feeData = await provider.getFeeData();
  const gasPrice = feeData.gasPrice || 0n;

  const cost = gasLimit * gasPrice;
  const costEth = formatEther(cost);

  return {
    cost: cost.toString(),
    costEth,
  };
}

// Gas optimization suggestions
export function getGasOptimizationTips(gasUsed: number): string[] {
  const tips: string[] = [];

  if (gasUsed > 1000000) {
    tips.push('Consider batching multiple operations');
  }

  if (gasUsed > 500000) {
    tips.push('Review storage operations - use memory when possible');
    tips.push('Consider using events instead of storage for logging');
  }

  if (gasUsed > 300000) {
    tips.push('Optimize loops and array operations');
  }

  tips.push('Use uint256 instead of smaller uint types');
  tips.push('Pack struct variables efficiently');
  tips.push('Use calldata instead of memory for read-only arrays');

  return tips;
}

// Compare gas costs
export interface GasComparison {
  estimatedGas: bigint;
  gasPrice: bigint;
  totalCost: bigint;
  totalCostEth: string;
}

export async function compareGasCosts(
  provider: BrowserProvider,
  operations: Array<{
    name: string;
    contractAddress: string;
    abi: any[];
    functionName: string;
    args: any[];
  }>
): Promise<Array<GasComparison & { name: string }>> {
  const feeData = await provider.getFeeData();
  const gasPrice = feeData.gasPrice || 0n;

  const results = await Promise.all(
    operations.map(async (op) => {
      const contract = new Contract(op.contractAddress, op.abi, provider);
      const estimatedGas = await contract[op.functionName].estimateGas(...op.args);
      const totalCost = estimatedGas * gasPrice;

      return {
        name: op.name,
        estimatedGas,
        gasPrice,
        totalCost,
        totalCostEth: formatEther(totalCost),
      };
    })
  );

  return results;
}

// Gas tracker hook
export function useGasTracker() {
  const { gasPrice, gasPriceGwei } = useCurrentGasPrice();
  const { maxFeePerGas, maxPriorityFeePerGas } = useEIP1559Fees();

  const getGasLevel = () => {
    if (!gasPriceGwei) return 'unknown';
    if (gasPriceGwei < 20) return 'low';
    if (gasPriceGwei < 50) return 'medium';
    if (gasPriceGwei < 100) return 'high';
    return 'very-high';
  };

  const getSavingsAdvice = () => {
    const level = getGasLevel();

    switch (level) {
      case 'low':
        return 'Great time to transact!';
      case 'medium':
        return 'Reasonable gas prices';
      case 'high':
        return 'Consider waiting for lower gas';
      case 'very-high':
        return 'Wait for gas to decrease if not urgent';
      default:
        return 'Loading gas data...';
    }
  };

  return {
    gasPrice,
    gasPriceGwei,
    maxFeePerGas,
    maxPriorityFeePerGas,
    gasLevel: getGasLevel(),
    savingsAdvice: getSavingsAdvice(),
  };
}

export default {
  useGasEstimate,
  useCurrentGasPrice,
  useEIP1559Fees,
  estimateGasWithEthers,
  calculateTransactionCost,
  getGasOptimizationTips,
  compareGasCosts,
  useGasTracker,
};
