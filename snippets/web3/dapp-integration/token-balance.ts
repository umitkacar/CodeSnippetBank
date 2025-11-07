/**
 * Token Balance Utilities
 * Fetch and display token balances
 */

import { useBalance, useReadContract } from 'wagmi';
import { formatUnits } from 'ethers';

const ERC20_ABI = [
  'function balanceOf(address) view returns (uint256)',
  'function decimals() view returns (uint8)',
  'function symbol() view returns (string)',
];

// Get native token balance (ETH, MATIC, etc.)
export function useNativeBalance(address: string) {
  const { data, isLoading, refetch } = useBalance({
    address: address as `0x${string}`,
  });

  return {
    balance: data?.value,
    formatted: data?.formatted,
    symbol: data?.symbol,
    decimals: data?.decimals,
    isLoading,
    refetch,
  };
}

// Get ERC20 token balance
export function useTokenBalance(tokenAddress: string, userAddress: string) {
  const { data: balance, isLoading: balanceLoading } = useReadContract({
    address: tokenAddress as `0x${string}`,
    abi: ERC20_ABI,
    functionName: 'balanceOf',
    args: [userAddress],
  });

  const { data: decimals, isLoading: decimalsLoading } = useReadContract({
    address: tokenAddress as `0x${string}`,
    abi: ERC20_ABI,
    functionName: 'decimals',
  });

  const { data: symbol, isLoading: symbolLoading } = useReadContract({
    address: tokenAddress as `0x${string}`,
    abi: ERC20_ABI,
    functionName: 'symbol',
  });

  const formatted = balance && decimals
    ? formatUnits(balance as bigint, decimals as number)
    : '0';

  return {
    balance: balance as bigint,
    formatted,
    symbol: symbol as string,
    decimals: decimals as number,
    isLoading: balanceLoading || decimalsLoading || symbolLoading,
  };
}

// Get multiple token balances
export function useMultiTokenBalances(
  tokens: Array<{ address: string; symbol?: string }>,
  userAddress: string
) {
  const balances = tokens.map((token) =>
    useTokenBalance(token.address, userAddress)
  );

  const isLoading = balances.some((b) => b.isLoading);

  return {
    balances: balances.map((b, index) => ({
      ...b,
      tokenAddress: tokens[index].address,
      symbol: b.symbol || tokens[index].symbol || 'UNKNOWN',
    })),
    isLoading,
  };
}

// Format balance for display
export function formatBalance(
  balance: bigint | undefined,
  decimals: number = 18,
  displayDecimals: number = 4
): string {
  if (!balance) return '0';

  const formatted = formatUnits(balance, decimals);
  const number = parseFloat(formatted);

  if (number === 0) return '0';
  if (number < 0.0001) return '< 0.0001';

  return number.toFixed(displayDecimals);
}

// Balance with USD value
export function useBalanceWithValue(
  tokenAddress: string,
  userAddress: string,
  priceUsd: number
) {
  const { balance, formatted, symbol, isLoading } = useTokenBalance(
    tokenAddress,
    userAddress
  );

  const usdValue = parseFloat(formatted) * priceUsd;

  return {
    balance,
    formatted,
    symbol,
    priceUsd,
    usdValue: usdValue.toFixed(2),
    isLoading,
  };
}

// Aggregate portfolio balance
export interface PortfolioToken {
  address: string;
  symbol: string;
  balance: string;
  priceUsd: number;
  valueUsd: number;
}

export function usePortfolioBalance(
  tokens: Array<{ address: string; priceUsd: number }>,
  userAddress: string
) {
  const balances = useMultiTokenBalances(tokens, userAddress);

  const portfolio: PortfolioToken[] = balances.balances.map((b, index) => ({
    address: tokens[index].address,
    symbol: b.symbol,
    balance: b.formatted,
    priceUsd: tokens[index].priceUsd,
    valueUsd: parseFloat(b.formatted) * tokens[index].priceUsd,
  }));

  const totalValue = portfolio.reduce((sum, token) => sum + token.valueUsd, 0);

  return {
    portfolio,
    totalValue: totalValue.toFixed(2),
    isLoading: balances.isLoading,
  };
}

// Balance display component
export function BalanceDisplay({
  tokenAddress,
  userAddress,
}: {
  tokenAddress: string;
  userAddress: string;
}) {
  const { formatted, symbol, isLoading } = useTokenBalance(tokenAddress, userAddress);

  if (isLoading) return <div>Loading balance...</div>;

  return (
    <div>
      <span>{formatted}</span> <span>{symbol}</span>
    </div>
  );
}

// Check if balance is sufficient
export function useHasSufficientBalance(
  tokenAddress: string,
  userAddress: string,
  requiredAmount: bigint
) {
  const { balance, isLoading } = useTokenBalance(tokenAddress, userAddress);

  const hasSufficient = balance ? balance >= requiredAmount : false;

  return {
    hasSufficient,
    balance,
    requiredAmount,
    deficit: balance && balance < requiredAmount ? requiredAmount - balance : 0n,
    isLoading,
  };
}

export default {
  useNativeBalance,
  useTokenBalance,
  useMultiTokenBalances,
  formatBalance,
  useBalanceWithValue,
  usePortfolioBalance,
  BalanceDisplay,
  useHasSufficientBalance,
};
