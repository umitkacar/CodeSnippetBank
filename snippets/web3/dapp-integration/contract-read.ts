/**
 * Contract Read Operations
 * Read data from smart contracts
 */

import { useReadContract, useReadContracts } from 'wagmi';
import { BrowserProvider, Contract } from 'ethers';

// ERC20 ABI snippet
const ERC20_ABI = [
  'function balanceOf(address) view returns (uint256)',
  'function totalSupply() view returns (uint256)',
  'function decimals() view returns (uint8)',
  'function symbol() view returns (string)',
  'function name() view returns (string)',
];

// Read single contract value
export function useTokenBalance(tokenAddress: string, userAddress: string) {
  const { data, isError, isLoading } = useReadContract({
    address: tokenAddress as `0x${string}`,
    abi: ERC20_ABI,
    functionName: 'balanceOf',
    args: [userAddress],
  });

  return {
    balance: data,
    isError,
    isLoading,
  };
}

// Read multiple values from single contract
export function useTokenInfo(tokenAddress: string) {
  const { data, isError, isLoading } = useReadContracts({
    contracts: [
      {
        address: tokenAddress as `0x${string}`,
        abi: ERC20_ABI,
        functionName: 'name',
      },
      {
        address: tokenAddress as `0x${string}`,
        abi: ERC20_ABI,
        functionName: 'symbol',
      },
      {
        address: tokenAddress as `0x${string}`,
        abi: ERC20_ABI,
        functionName: 'decimals',
      },
      {
        address: tokenAddress as `0x${string}`,
        abi: ERC20_ABI,
        functionName: 'totalSupply',
      },
    ],
  });

  return {
    name: data?.[0]?.result,
    symbol: data?.[1]?.result,
    decimals: data?.[2]?.result,
    totalSupply: data?.[3]?.result,
    isError,
    isLoading,
  };
}

// Read with ethers.js
export async function readContractWithEthers(
  provider: BrowserProvider,
  contractAddress: string,
  abi: any[],
  functionName: string,
  args: any[] = []
) {
  const contract = new Contract(contractAddress, abi, provider);
  return await contract[functionName](...args);
}

// Read multiple contracts
export async function readMultipleContracts(
  provider: BrowserProvider,
  calls: Array<{
    address: string;
    abi: any[];
    functionName: string;
    args?: any[];
  }>
) {
  const results = await Promise.all(
    calls.map(async (call) => {
      const contract = new Contract(call.address, call.abi, provider);
      return await contract[call.functionName](...(call.args || []));
    })
  );

  return results;
}

// Custom hook for contract view function
export function useContractView<T>(
  address: string,
  abi: any[],
  functionName: string,
  args?: any[]
) {
  const { data, isError, isLoading, refetch } = useReadContract({
    address: address as `0x${string}`,
    abi,
    functionName,
    args,
  });

  return {
    data: data as T,
    isError,
    isLoading,
    refetch,
  };
}

export default {
  useTokenBalance,
  useTokenInfo,
  readContractWithEthers,
  readMultipleContracts,
  useContractView,
};
