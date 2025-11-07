/**
 * Multicall Pattern
 * Batch multiple contract calls into a single request
 */

import { useReadContracts } from 'wagmi';
import { BrowserProvider, Contract } from 'ethers';

// Multicall with wagmi
export function useMulticall(calls: Array<{
  address: string;
  abi: any[];
  functionName: string;
  args?: any[];
}>) {
  const { data, isLoading, isError, refetch } = useReadContracts({
    contracts: calls.map((call) => ({
      address: call.address as `0x${string}`,
      abi: call.abi,
      functionName: call.functionName,
      args: call.args,
    })),
  });

  return {
    data: data?.map((result) => result.result),
    isLoading,
    isError,
    refetch,
  };
}

// Token info multicall
export function useTokenMulticall(tokenAddresses: string[]) {
  const ERC20_ABI = [
    'function name() view returns (string)',
    'function symbol() view returns (string)',
    'function decimals() view returns (uint8)',
    'function totalSupply() view returns (uint256)',
  ];

  const calls = tokenAddresses.flatMap((address) => [
    { address, abi: ERC20_ABI, functionName: 'name' },
    { address, abi: ERC20_ABI, functionName: 'symbol' },
    { address, abi: ERC20_ABI, functionName: 'decimals' },
    { address, abi: ERC20_ABI, functionName: 'totalSupply' },
  ]);

  const { data, isLoading, isError } = useMulticall(calls);

  // Group results by token
  const tokens = [];
  if (data) {
    for (let i = 0; i < data.length; i += 4) {
      tokens.push({
        address: tokenAddresses[i / 4],
        name: data[i],
        symbol: data[i + 1],
        decimals: data[i + 2],
        totalSupply: data[i + 3],
      });
    }
  }

  return {
    tokens,
    isLoading,
    isError,
  };
}

// Balance multicall for multiple tokens
export function useMultiTokenBalance(
  tokenAddresses: string[],
  userAddress: string
) {
  const ERC20_ABI = ['function balanceOf(address) view returns (uint256)'];

  const calls = tokenAddresses.map((address) => ({
    address,
    abi: ERC20_ABI,
    functionName: 'balanceOf',
    args: [userAddress],
  }));

  const { data, isLoading, isError, refetch } = useMulticall(calls);

  const balances = tokenAddresses.map((address, index) => ({
    token: address,
    balance: data?.[index],
  }));

  return {
    balances,
    isLoading,
    isError,
    refetch,
  };
}

// Generic multicall with ethers.js
export async function multicallWithEthers(
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

// Multicall with custom aggregator
export async function aggregatedMulticall<T>(
  provider: BrowserProvider,
  calls: Array<{
    address: string;
    abi: any[];
    functionName: string;
    args?: any[];
  }>,
  aggregator: (results: any[]) => T
): Promise<T> {
  const results = await multicallWithEthers(provider, calls);
  return aggregator(results);
}

// Portfolio value multicall example
export interface TokenBalance {
  token: string;
  balance: bigint;
  price: bigint;
  value: bigint;
}

export function usePortfolioValue(
  tokens: Array<{ address: string; priceOracle: string }>,
  userAddress: string
) {
  const calls = tokens.flatMap((token) => [
    {
      address: token.address,
      abi: ['function balanceOf(address) view returns (uint256)'],
      functionName: 'balanceOf',
      args: [userAddress],
    },
    {
      address: token.priceOracle,
      abi: ['function getPrice(address) view returns (uint256)'],
      functionName: 'getPrice',
      args: [token.address],
    },
  ]);

  const { data, isLoading, isError } = useMulticall(calls);

  let totalValue = 0n;
  const positions: TokenBalance[] = [];

  if (data) {
    for (let i = 0; i < data.length; i += 2) {
      const balance = data[i] as bigint;
      const price = data[i + 1] as bigint;
      const value = (balance * price) / BigInt(1e18);

      positions.push({
        token: tokens[i / 2].address,
        balance,
        price,
        value,
      });

      totalValue += value;
    }
  }

  return {
    positions,
    totalValue,
    isLoading,
    isError,
  };
}

export default {
  useMulticall,
  useTokenMulticall,
  useMultiTokenBalance,
  multicallWithEthers,
  aggregatedMulticall,
  usePortfolioValue,
};
