/**
 * Uniswap V3 Swap Integration
 * Execute swaps on Uniswap V3
 */

import { BrowserProvider, Contract } from 'ethers';
import { useWriteContract, useWaitForTransactionReceipt } from 'wagmi';

const UNISWAP_V3_ROUTER_ABI = [
  'function exactInputSingle((address tokenIn, address tokenOut, uint24 fee, address recipient, uint256 deadline, uint256 amountIn, uint256 amountOutMinimum, uint160 sqrtPriceLimitX96)) external payable returns (uint256 amountOut)',
  'function exactOutputSingle((address tokenIn, address tokenOut, uint24 fee, address recipient, uint256 deadline, uint256 amountOut, uint256 amountInMaximum, uint160 sqrtPriceLimitX96)) external payable returns (uint256 amountIn)',
];

const UNISWAP_V3_ROUTER_ADDRESS = '0xE592427A0AEce92De3Edee1F18E0157C05861564';

export interface SwapParams {
  tokenIn: string;
  tokenOut: string;
  fee: number; // 500, 3000, or 10000
  amountIn: bigint;
  amountOutMinimum: bigint;
  recipient: string;
  deadline: number;
}

// Hook for Uniswap V3 swap
export function useUniswapV3Swap() {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const swap = async (params: SwapParams) => {
    writeContract({
      address: UNISWAP_V3_ROUTER_ADDRESS as `0x${string}`,
      abi: UNISWAP_V3_ROUTER_ABI,
      functionName: 'exactInputSingle',
      args: [
        {
          tokenIn: params.tokenIn,
          tokenOut: params.tokenOut,
          fee: params.fee,
          recipient: params.recipient,
          deadline: params.deadline,
          amountIn: params.amountIn,
          amountOutMinimum: params.amountOutMinimum,
          sqrtPriceLimitX96: 0n,
        },
      ],
    });
  };

  return {
    swap,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Execute swap with ethers.js
export async function executeUniswapV3Swap(
  provider: BrowserProvider,
  params: SwapParams
): Promise<any> {
  const signer = await provider.getSigner();
  const router = new Contract(UNISWAP_V3_ROUTER_ADDRESS, UNISWAP_V3_ROUTER_ABI, signer);

  const tx = await router.exactInputSingle({
    tokenIn: params.tokenIn,
    tokenOut: params.tokenOut,
    fee: params.fee,
    recipient: params.recipient,
    deadline: params.deadline,
    amountIn: params.amountIn,
    amountOutMinimum: params.amountOutMinimum,
    sqrtPriceLimitX96: 0,
  });

  return await tx.wait();
}

// Get quote from Uniswap V3 Quoter
const QUOTER_ABI = [
  'function quoteExactInputSingle(address tokenIn, address tokenOut, uint24 fee, uint256 amountIn, uint160 sqrtPriceLimitX96) external returns (uint256 amountOut)',
];

const QUOTER_ADDRESS = '0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6';

export async function getUniswapV3Quote(
  provider: BrowserProvider,
  tokenIn: string,
  tokenOut: string,
  fee: number,
  amountIn: bigint
): Promise<bigint> {
  const quoter = new Contract(QUOTER_ADDRESS, QUOTER_ABI, provider);
  const amountOut = await quoter.quoteExactInputSingle.staticCall(
    tokenIn,
    tokenOut,
    fee,
    amountIn,
    0
  );
  return amountOut;
}

// Calculate price impact
export function calculatePriceImpact(
  expectedOutput: bigint,
  actualOutput: bigint
): number {
  const impact = Number(expectedOutput - actualOutput) / Number(expectedOutput);
  return impact * 100;
}

export default {
  useUniswapV3Swap,
  executeUniswapV3Swap,
  getUniswapV3Quote,
  calculatePriceImpact,
  UNISWAP_V3_ROUTER_ADDRESS,
};
