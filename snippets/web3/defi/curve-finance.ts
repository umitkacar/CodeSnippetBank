/**
 * Curve Finance Integration
 * Stablecoin swaps and liquidity provision
 */

import { BrowserProvider, Contract } from 'ethers';
import { useWriteContract, useWaitForTransactionReceipt } from 'wagmi';

const CURVE_POOL_ABI = [
  'function exchange(int128 i, int128 j, uint256 dx, uint256 min_dy) external returns (uint256)',
  'function add_liquidity(uint256[3] calldata amounts, uint256 min_mint_amount) external returns (uint256)',
  'function remove_liquidity(uint256 amount, uint256[3] calldata min_amounts) external returns (uint256[3])',
  'function remove_liquidity_one_coin(uint256 token_amount, int128 i, uint256 min_amount) external returns (uint256)',
  'function get_dy(int128 i, int128 j, uint256 dx) external view returns (uint256)',
  'function balances(uint256 i) external view returns (uint256)',
];

// Curve 3pool (DAI/USDC/USDT)
const CURVE_3POOL = '0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7';

// Swap on Curve
export function useCurveSwap(poolAddress: string = CURVE_3POOL) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const swap = async (
    fromIndex: number,
    toIndex: number,
    amount: bigint,
    minAmount: bigint
  ) => {
    writeContract({
      address: poolAddress as `0x${string}`,
      abi: CURVE_POOL_ABI,
      functionName: 'exchange',
      args: [fromIndex, toIndex, amount, minAmount],
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

// Add liquidity to Curve pool
export function useCurveAddLiquidity(poolAddress: string = CURVE_3POOL) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const addLiquidity = async (amounts: bigint[], minMintAmount: bigint) => {
    writeContract({
      address: poolAddress as `0x${string}`,
      abi: CURVE_POOL_ABI,
      functionName: 'add_liquidity',
      args: [amounts, minMintAmount],
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
export function useCurveRemoveLiquidity(poolAddress: string = CURVE_3POOL) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const removeLiquidity = async (amount: bigint, minAmounts: bigint[]) => {
    writeContract({
      address: poolAddress as `0x${string}`,
      abi: CURVE_POOL_ABI,
      functionName: 'remove_liquidity',
      args: [amount, minAmounts],
    });
  };

  const removeLiquidityOneCoin = async (
    amount: bigint,
    coinIndex: number,
    minAmount: bigint
  ) => {
    writeContract({
      address: poolAddress as `0x${string}`,
      abi: CURVE_POOL_ABI,
      functionName: 'remove_liquidity_one_coin',
      args: [amount, coinIndex, minAmount],
    });
  };

  return {
    removeLiquidity,
    removeLiquidityOneCoin,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Get swap output estimate
export async function getCurveSwapOutput(
  provider: BrowserProvider,
  poolAddress: string,
  fromIndex: number,
  toIndex: number,
  amount: bigint
): Promise<bigint> {
  const pool = new Contract(poolAddress, CURVE_POOL_ABI, provider);
  return await pool.get_dy(fromIndex, toIndex, amount);
}

// Get pool balances
export async function getCurvePoolBalances(
  provider: BrowserProvider,
  poolAddress: string,
  coinCount: number = 3
): Promise<bigint[]> {
  const pool = new Contract(poolAddress, CURVE_POOL_ABI, provider);

  const balances = await Promise.all(
    Array.from({ length: coinCount }, (_, i) => pool.balances(i))
  );

  return balances;
}

export default {
  useCurveSwap,
  useCurveAddLiquidity,
  useCurveRemoveLiquidity,
  getCurveSwapOutput,
  getCurvePoolBalances,
  CURVE_3POOL,
};
