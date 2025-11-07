/**
 * Total Value Locked (TVL) Calculator
 * Calculate TVL across DeFi protocols
 */

import { BrowserProvider, Contract } from 'ethers';

export interface TVLData {
  protocol: string;
  tvl: number;
  assets: Array<{ token: string; amount: bigint; valueUSD: number }>;
}

// Calculate pool TVL
export async function calculatePoolTVL(
  provider: BrowserProvider,
  poolAddress: string,
  token0Address: string,
  token1Address: string,
  token0Price: number,
  token1Price: number
): Promise<number> {
  const PAIR_ABI = [
    'function getReserves() external view returns (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast)',
    'function token0() external view returns (address)',
    'function decimals() external view returns (uint8)',
  ];

  const pair = new Contract(poolAddress, PAIR_ABI, provider);
  const reserves = await pair.getReserves();

  const reserve0USD = (Number(reserves[0]) / 1e18) * token0Price;
  const reserve1USD = (Number(reserves[1]) / 1e18) * token1Price;

  return reserve0USD + reserve1USD;
}

// Calculate lending protocol TVL
export async function calculateLendingTVL(
  provider: BrowserProvider,
  markets: Array<{ address: string; price: number }>
): Promise<number> {
  const MARKET_ABI = [
    'function totalSupply() external view returns (uint256)',
    'function exchangeRateStored() external view returns (uint256)',
  ];

  let totalTVL = 0;

  for (const market of markets) {
    const contract = new Contract(market.address, MARKET_ABI, provider);
    const [totalSupply, exchangeRate] = await Promise.all([
      contract.totalSupply(),
      contract.exchangeRateStored(),
    ]);

    const underlying = (Number(totalSupply) * Number(exchangeRate)) / 1e18;
    totalTVL += (underlying / 1e18) * market.price;
  }

  return totalTVL;
}

// Calculate staking TVL
export async function calculateStakingTVL(
  provider: BrowserProvider,
  stakingAddress: string,
  tokenPrice: number
): Promise<number> {
  const STAKING_ABI = ['function totalSupply() external view returns (uint256)'];

  const staking = new Contract(stakingAddress, STAKING_ABI, provider);
  const totalStaked = await staking.totalSupply();

  return (Number(totalStaked) / 1e18) * tokenPrice;
}

// Aggregate protocol TVL
export async function aggregateProtocolTVL(
  provider: BrowserProvider,
  protocol: {
    name: string;
    pools: Array<{ address: string; token0Price: number; token1Price: number }>;
    lending?: Array<{ address: string; price: number }>;
    staking?: Array<{ address: string; price: number }>;
  }
): Promise<TVLData> {
  let totalTVL = 0;
  const assets: Array<{ token: string; amount: bigint; valueUSD: number }> = [];

  // Calculate pool TVL
  for (const pool of protocol.pools) {
    const tvl = await calculatePoolTVL(
      provider,
      pool.address,
      pool.address,
      pool.address,
      pool.token0Price,
      pool.token1Price
    );
    totalTVL += tvl;
  }

  // Calculate lending TVL
  if (protocol.lending) {
    const lendingTVL = await calculateLendingTVL(provider, protocol.lending);
    totalTVL += lendingTVL;
  }

  // Calculate staking TVL
  if (protocol.staking) {
    for (const stake of protocol.staking) {
      const stakingTVL = await calculateStakingTVL(
        provider,
        stake.address,
        stake.price
      );
      totalTVL += stakingTVL;
    }
  }

  return {
    protocol: protocol.name,
    tvl: totalTVL,
    assets,
  };
}

// TVL change percentage
export function calculateTVLChange(
  currentTVL: number,
  previousTVL: number
): { change: number; percentage: number } {
  const change = currentTVL - previousTVL;
  const percentage = (change / previousTVL) * 100;

  return { change, percentage };
}

// Market dominance
export function calculateMarketDominance(
  protocolTVL: number,
  totalMarketTVL: number
): number {
  return (protocolTVL / totalMarketTVL) * 100;
}

export default {
  calculatePoolTVL,
  calculateLendingTVL,
  calculateStakingTVL,
  aggregateProtocolTVL,
  calculateTVLChange,
  calculateMarketDominance,
};
