/**
 * Wallet Balance Tracker
 * Track and monitor wallet balances across chains
 */

import { useBalance, useReadContracts } from 'wagmi';
import { useState, useEffect } from 'react';
import { formatUnits } from 'ethers';

const ERC20_ABI = [
  'function balanceOf(address) view returns (uint256)',
  'function decimals() view returns (uint8)',
  'function symbol() view returns (string)',
  'function name() view returns (string)',
];

export interface TokenBalance {
  address: string;
  symbol: string;
  name: string;
  balance: bigint;
  formatted: string;
  decimals: number;
  priceUsd?: number;
  valueUsd?: number;
}

// Track multiple token balances
export function usePortfolioTracker(
  tokens: Array<{ address: string; chainId?: number }>,
  userAddress: string
) {
  const [balances, setBalances] = useState<TokenBalance[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const calls = tokens.flatMap((token) => [
    {
      address: token.address as `0x${string}`,
      abi: ERC20_ABI,
      functionName: 'symbol',
    },
    {
      address: token.address as `0x${string}`,
      abi: ERC20_ABI,
      functionName: 'name',
    },
    {
      address: token.address as `0x${string}`,
      abi: ERC20_ABI,
      functionName: 'decimals',
    },
    {
      address: token.address as `0x${string}`,
      abi: ERC20_ABI,
      functionName: 'balanceOf',
      args: [userAddress],
    },
  ]);

  const { data, isLoading: contractsLoading } = useReadContracts({
    contracts: calls,
  });

  useEffect(() => {
    if (data && !contractsLoading) {
      const parsedBalances: TokenBalance[] = [];

      for (let i = 0; i < data.length; i += 4) {
        const symbol = data[i]?.result as string;
        const name = data[i + 1]?.result as string;
        const decimals = data[i + 2]?.result as number;
        const balance = data[i + 3]?.result as bigint;

        if (balance !== undefined && decimals !== undefined) {
          parsedBalances.push({
            address: tokens[i / 4].address,
            symbol,
            name,
            balance,
            formatted: formatUnits(balance, decimals),
            decimals,
          });
        }
      }

      setBalances(parsedBalances);
      setIsLoading(false);
    }
  }, [data, contractsLoading, tokens]);

  return {
    balances,
    isLoading,
  };
}

// Real-time balance watcher
export function useBalanceWatcher(
  tokenAddress: string,
  userAddress: string,
  onBalanceChange?: (newBalance: bigint, oldBalance: bigint) => void
) {
  const [previousBalance, setPreviousBalance] = useState<bigint>(0n);

  const { data: balanceData, refetch } = useReadContracts({
    contracts: [
      {
        address: tokenAddress as `0x${string}`,
        abi: ERC20_ABI,
        functionName: 'balanceOf',
        args: [userAddress],
      },
      {
        address: tokenAddress as `0x${string}`,
        abi: ERC20_ABI,
        functionName: 'decimals',
      },
    ],
  });

  const balance = balanceData?.[0]?.result as bigint;
  const decimals = balanceData?.[1]?.result as number;

  useEffect(() => {
    if (balance !== undefined && balance !== previousBalance) {
      if (onBalanceChange && previousBalance !== 0n) {
        onBalanceChange(balance, previousBalance);
      }
      setPreviousBalance(balance);
    }
  }, [balance, previousBalance, onBalanceChange]);

  // Poll every 10 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      refetch();
    }, 10000);

    return () => clearInterval(interval);
  }, [refetch]);

  return {
    balance,
    formatted: balance && decimals ? formatUnits(balance, decimals) : '0',
    decimals,
    refetch,
  };
}

// Native balance tracker
export function useNativeBalanceTracker(
  address: string,
  onBalanceChange?: (newBalance: bigint, oldBalance: bigint) => void
) {
  const [previousBalance, setPreviousBalance] = useState<bigint>(0n);

  const { data, refetch } = useBalance({
    address: address as `0x${string}`,
  });

  useEffect(() => {
    if (data?.value !== undefined && data.value !== previousBalance) {
      if (onBalanceChange && previousBalance !== 0n) {
        onBalanceChange(data.value, previousBalance);
      }
      setPreviousBalance(data.value);
    }
  }, [data?.value, previousBalance, onBalanceChange]);

  // Poll every 10 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      refetch();
    }, 10000);

    return () => clearInterval(interval);
  }, [refetch]);

  return {
    balance: data?.value,
    formatted: data?.formatted,
    symbol: data?.symbol,
    refetch,
  };
}

// Balance notification component
export function BalanceNotification({
  tokenAddress,
  userAddress,
}: {
  tokenAddress: string;
  userAddress: string;
}) {
  const [notification, setNotification] = useState<string | null>(null);

  const handleBalanceChange = (newBalance: bigint, oldBalance: bigint) => {
    const diff = newBalance - oldBalance;
    if (diff > 0n) {
      setNotification(`+${formatUnits(diff, 18)} tokens received`);
    } else if (diff < 0n) {
      setNotification(`${formatUnits(-diff, 18)} tokens sent`);
    }

    // Clear notification after 5 seconds
    setTimeout(() => setNotification(null), 5000);
  };

  useBalanceWatcher(tokenAddress, userAddress, handleBalanceChange);

  if (!notification) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        backgroundColor: '#10b981',
        color: 'white',
        padding: '12px 20px',
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
      }}
    >
      {notification}
    </div>
  );
}

// Portfolio summary
export function usePortfolioSummary(
  balances: TokenBalance[],
  prices: Record<string, number>
) {
  const [summary, setSummary] = useState({
    totalValueUsd: 0,
    largestHolding: null as TokenBalance | null,
    tokenCount: 0,
  });

  useEffect(() => {
    let total = 0;
    let largest: TokenBalance | null = null;
    let largestValue = 0;

    balances.forEach((token) => {
      const price = prices[token.address.toLowerCase()] || 0;
      const value = parseFloat(token.formatted) * price;
      total += value;

      if (value > largestValue) {
        largestValue = value;
        largest = { ...token, priceUsd: price, valueUsd: value };
      }
    });

    setSummary({
      totalValueUsd: total,
      largestHolding: largest,
      tokenCount: balances.length,
    });
  }, [balances, prices]);

  return summary;
}

export default {
  usePortfolioTracker,
  useBalanceWatcher,
  useNativeBalanceTracker,
  BalanceNotification,
  usePortfolioSummary,
};
