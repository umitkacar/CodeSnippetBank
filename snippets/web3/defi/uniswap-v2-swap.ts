/**
 * Uniswap V2 Swap Integration
 * Execute swaps on Uniswap V2 and forks (SushiSwap, PancakeSwap)
 */

import { BrowserProvider, Contract } from 'ethers';
import { useWriteContract, useWaitForTransactionReceipt } from 'wagmi';

const UNISWAP_V2_ROUTER_ABI = [
  'function swapExactTokensForTokens(uint amountIn, uint amountOutMin, address[] calldata path, address to, uint deadline) external returns (uint[] memory amounts)',
  'function swapTokensForExactTokens(uint amountOut, uint amountInMax, address[] calldata path, address to, uint deadline) external returns (uint[] memory amounts)',
  'function swapExactETHForTokens(uint amountOutMin, address[] calldata path, address to, uint deadline) external payable returns (uint[] memory amounts)',
  'function swapExactTokensForETH(uint amountIn, uint amountOutMin, address[] calldata path, address to, uint deadline) external returns (uint[] memory amounts)',
  'function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts)',
  'function getAmountsIn(uint amountOut, address[] calldata path) external view returns (uint[] memory amounts)',
];

const UNISWAP_V2_ROUTER_ADDRESS = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D';
const WETH_ADDRESS = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2';

// Swap exact tokens for tokens
export function useUniswapV2Swap(routerAddress: string = UNISWAP_V2_ROUTER_ADDRESS) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const swapExactTokensForTokens = async (
    amountIn: bigint,
    amountOutMin: bigint,
    path: string[],
    to: string,
    deadline: number
  ) => {
    writeContract({
      address: routerAddress as `0x${string}`,
      abi: UNISWAP_V2_ROUTER_ABI,
      functionName: 'swapExactTokensForTokens',
      args: [amountIn, amountOutMin, path, to, deadline],
    });
  };

  const swapExactETHForTokens = async (
    amountOutMin: bigint,
    path: string[],
    to: string,
    deadline: number,
    value: bigint
  ) => {
    writeContract({
      address: routerAddress as `0x${string}`,
      abi: UNISWAP_V2_ROUTER_ABI,
      functionName: 'swapExactETHForTokens',
      args: [amountOutMin, path, to, deadline],
      value,
    });
  };

  return {
    swapExactTokensForTokens,
    swapExactETHForTokens,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Get amounts out (quote)
export async function getUniswapV2Quote(
  provider: BrowserProvider,
  amountIn: bigint,
  path: string[],
  routerAddress: string = UNISWAP_V2_ROUTER_ADDRESS
): Promise<bigint[]> {
  const router = new Contract(routerAddress, UNISWAP_V2_ROUTER_ABI, provider);
  const amounts = await router.getAmountsOut(amountIn, path);
  return amounts;
}

// Create token path for swap
export function createSwapPath(
  tokenIn: string,
  tokenOut: string,
  useWETH: boolean = true
): string[] {
  if (!useWETH || tokenIn === WETH_ADDRESS || tokenOut === WETH_ADDRESS) {
    return [tokenIn, tokenOut];
  }

  // Route through WETH for better liquidity
  return [tokenIn, WETH_ADDRESS, tokenOut];
}

// Calculate minimum amount out with slippage
export function calculateMinAmountOut(
  amountOut: bigint,
  slippagePercent: number
): bigint {
  const slippage = BigInt(Math.floor(slippagePercent * 100));
  return (amountOut * (10000n - slippage)) / 10000n;
}

// Get deadline timestamp
export function getDeadline(minutesFromNow: number = 30): number {
  return Math.floor(Date.now() / 1000) + minutesFromNow * 60;
}

// Multi-hop swap path finder
export async function findBestPath(
  provider: BrowserProvider,
  tokenIn: string,
  tokenOut: string,
  amountIn: bigint,
  intermediateTokens: string[] = [WETH_ADDRESS]
): Promise<{ path: string[]; amountOut: bigint }> {
  const router = new Contract(
    UNISWAP_V2_ROUTER_ADDRESS,
    UNISWAP_V2_ROUTER_ABI,
    provider
  );

  // Try direct path
  const directPath = [tokenIn, tokenOut];
  let bestPath = directPath;
  let bestAmountOut = 0n;

  try {
    const [, amountOut] = await router.getAmountsOut(amountIn, directPath);
    bestAmountOut = amountOut;
  } catch (error) {
    // Direct path doesn't exist
  }

  // Try paths through intermediate tokens
  for (const intermediate of intermediateTokens) {
    if (intermediate === tokenIn || intermediate === tokenOut) continue;

    const path = [tokenIn, intermediate, tokenOut];

    try {
      const amounts = await router.getAmountsOut(amountIn, path);
      const amountOut = amounts[amounts.length - 1];

      if (amountOut > bestAmountOut) {
        bestAmountOut = amountOut;
        bestPath = path;
      }
    } catch (error) {
      // Path doesn't exist
    }
  }

  return { path: bestPath, amountOut: bestAmountOut };
}

export default {
  useUniswapV2Swap,
  getUniswapV2Quote,
  createSwapPath,
  calculateMinAmountOut,
  getDeadline,
  findBestPath,
  UNISWAP_V2_ROUTER_ADDRESS,
  WETH_ADDRESS,
};
