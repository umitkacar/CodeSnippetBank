/**
 * Perpetual Futures Trading
 * Leveraged trading on decentralized exchanges
 */

import { BrowserProvider, Contract } from 'ethers';
import { useWriteContract, useWaitForTransactionReceipt } from 'wagmi';

const PERP_MARKET_ABI = [
  'function openPosition(address baseToken, bool isBaseToQuote, bool isExactInput, uint256 amount, uint256 oppositeAmountBound, uint256 deadline, uint160 sqrtPriceLimitX96, bytes32 referralCode) external returns (uint256 base, uint256 quote)',
  'function closePosition((address baseToken, uint160 sqrtPriceLimitX96, uint256 oppositeAmountBound, uint256 deadline, bytes32 referralCode) params) external returns (uint256 base, uint256 quote)',
  'function addLiquidity((address baseToken, uint256 base, uint256 quote, int24 lowerTick, int24 upperTick, uint256 minBase, uint256 minQuote, bool useTakerBalance, uint256 deadline) params) external returns (uint128 liquidity)',
];

// Open perpetual position
export function useOpenPerpPosition(marketAddress: string) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const openPosition = async (
    baseToken: string,
    isLong: boolean,
    amount: bigint,
    leverage: number,
    slippage: bigint,
    deadline: number
  ) => {
    writeContract({
      address: marketAddress as `0x${string}`,
      abi: PERP_MARKET_ABI,
      functionName: 'openPosition',
      args: [
        baseToken,
        !isLong, // isBaseToQuote
        true, // isExactInput
        amount,
        slippage,
        deadline,
        0n, // sqrtPriceLimitX96
        '0x0000000000000000000000000000000000000000000000000000000000000000',
      ],
    });
  };

  return {
    openPosition,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Close perpetual position
export function useClosePerpPosition(marketAddress: string) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const closePosition = async (
    baseToken: string,
    slippage: bigint,
    deadline: number
  ) => {
    writeContract({
      address: marketAddress as `0x${string}`,
      abi: PERP_MARKET_ABI,
      functionName: 'closePosition',
      args: [
        {
          baseToken,
          sqrtPriceLimitX96: 0n,
          oppositeAmountBound: slippage,
          deadline,
          referralCode:
            '0x0000000000000000000000000000000000000000000000000000000000000000',
        },
      ],
    });
  };

  return {
    closePosition,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Calculate liquidation price
export function calculateLiquidationPrice(
  entryPrice: number,
  leverage: number,
  isLong: boolean,
  maintenanceMargin: number = 0.0625 // 6.25%
): number {
  if (isLong) {
    return entryPrice * (1 - 1 / leverage + maintenanceMargin);
  } else {
    return entryPrice * (1 + 1 / leverage - maintenanceMargin);
  }
}

// Calculate PnL
export function calculatePnL(
  entryPrice: number,
  currentPrice: number,
  size: number,
  isLong: boolean
): { pnl: number; pnlPercentage: number } {
  const priceDiff = isLong ? currentPrice - entryPrice : entryPrice - currentPrice;
  const pnl = priceDiff * size;
  const pnlPercentage = (priceDiff / entryPrice) * 100;

  return { pnl, pnlPercentage };
}

export default {
  useOpenPerpPosition,
  useClosePerpPosition,
  calculateLiquidationPrice,
  calculatePnL,
};
