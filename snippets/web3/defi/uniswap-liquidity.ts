/**
 * Uniswap V2 Liquidity Management
 * Add and remove liquidity from Uniswap V2 pools
 */

import { BrowserProvider, Contract } from 'ethers';
import { useWriteContract, useWaitForTransactionReceipt, useReadContract } from 'wagmi';

const UNISWAP_V2_ROUTER_ABI = [
  'function addLiquidity(address tokenA, address tokenB, uint amountADesired, uint amountBDesired, uint amountAMin, uint amountBMin, address to, uint deadline) external returns (uint amountA, uint amountB, uint liquidity)',
  'function removeLiquidity(address tokenA, address tokenB, uint liquidity, uint amountAMin, uint amountBMin, address to, uint deadline) external returns (uint amountA, uint amountB)',
];

const PAIR_ABI = [
  'function getReserves() external view returns (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast)',
  'function token0() external view returns (address)',
  'function token1() external view returns (address)',
  'function totalSupply() external view returns (uint)',
  'function balanceOf(address) external view returns (uint)',
];

const FACTORY_ABI = [
  'function getPair(address tokenA, address tokenB) external view returns (address pair)',
];

const UNISWAP_V2_ROUTER = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D';
const UNISWAP_V2_FACTORY = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f';

// Add liquidity
export function useAddLiquidity() {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const addLiquidity = async (
    tokenA: string,
    tokenB: string,
    amountADesired: bigint,
    amountBDesired: bigint,
    amountAMin: bigint,
    amountBMin: bigint,
    to: string,
    deadline: number
  ) => {
    writeContract({
      address: UNISWAP_V2_ROUTER as `0x${string}`,
      abi: UNISWAP_V2_ROUTER_ABI,
      functionName: 'addLiquidity',
      args: [
        tokenA,
        tokenB,
        amountADesired,
        amountBDesired,
        amountAMin,
        amountBMin,
        to,
        deadline,
      ],
    });
  };

  return {
    addLiquidity,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Remove liquidity
export function useRemoveLiquidity() {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const removeLiquidity = async (
    tokenA: string,
    tokenB: string,
    liquidity: bigint,
    amountAMin: bigint,
    amountBMin: bigint,
    to: string,
    deadline: number
  ) => {
    writeContract({
      address: UNISWAP_V2_ROUTER as `0x${string}`,
      abi: UNISWAP_V2_ROUTER_ABI,
      functionName: 'removeLiquidity',
      args: [tokenA, tokenB, liquidity, amountAMin, amountBMin, to, deadline],
    });
  };

  return {
    removeLiquidity,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Get pair address
export async function getPairAddress(
  provider: BrowserProvider,
  tokenA: string,
  tokenB: string
): Promise<string> {
  const factory = new Contract(UNISWAP_V2_FACTORY, FACTORY_ABI, provider);
  return await factory.getPair(tokenA, tokenB);
}

// Get pair reserves
export async function getPairReserves(
  provider: BrowserProvider,
  pairAddress: string
): Promise<{ reserve0: bigint; reserve1: bigint; token0: string; token1: string }> {
  const pair = new Contract(pairAddress, PAIR_ABI, provider);

  const [reserves, token0, token1] = await Promise.all([
    pair.getReserves(),
    pair.token0(),
    pair.token1(),
  ]);

  return {
    reserve0: reserves[0],
    reserve1: reserves[1],
    token0,
    token1,
  };
}

// Calculate optimal amounts for adding liquidity
export async function calculateOptimalAmounts(
  provider: BrowserProvider,
  tokenA: string,
  tokenB: string,
  amountADesired: bigint,
  amountBDesired: bigint
): Promise<{ amountA: bigint; amountB: bigint }> {
  const pairAddress = await getPairAddress(provider, tokenA, tokenB);

  if (pairAddress === '0x0000000000000000000000000000000000000000') {
    // New pair, return desired amounts
    return { amountA: amountADesired, amountB: amountBDesired };
  }

  const { reserve0, reserve1, token0 } = await getPairReserves(provider, pairAddress);

  const [reserveA, reserveB] =
    tokenA.toLowerCase() === token0.toLowerCase()
      ? [reserve0, reserve1]
      : [reserve1, reserve0];

  const amountBOptimal = (amountADesired * reserveB) / reserveA;

  if (amountBOptimal <= amountBDesired) {
    return { amountA: amountADesired, amountB: amountBOptimal };
  }

  const amountAOptimal = (amountBDesired * reserveA) / reserveB;

  return { amountA: amountAOptimal, amountB: amountBDesired };
}

// Get LP token balance
export function useLPBalance(pairAddress: string, userAddress: string) {
  const { data: balance, isLoading, refetch } = useReadContract({
    address: pairAddress as `0x${string}`,
    abi: PAIR_ABI,
    functionName: 'balanceOf',
    args: [userAddress],
  });

  return {
    balance: balance as bigint,
    isLoading,
    refetch,
  };
}

// Calculate share of pool
export async function calculatePoolShare(
  provider: BrowserProvider,
  pairAddress: string,
  lpBalance: bigint
): Promise<number> {
  const pair = new Contract(pairAddress, PAIR_ABI, provider);
  const totalSupply = await pair.totalSupply();

  return Number((lpBalance * 10000n) / totalSupply) / 100;
}

export default {
  useAddLiquidity,
  useRemoveLiquidity,
  getPairAddress,
  getPairReserves,
  calculateOptimalAmounts,
  useLPBalance,
  calculatePoolShare,
  UNISWAP_V2_ROUTER,
  UNISWAP_V2_FACTORY,
};
