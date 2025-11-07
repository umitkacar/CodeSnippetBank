/**
 * DeFi Price Oracles
 * Chainlink and other oracle integrations
 */

import { BrowserProvider, Contract } from 'ethers';
import { useReadContract } from 'wagmi';

const CHAINLINK_PRICE_FEED_ABI = [
  'function latestRoundData() external view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)',
  'function decimals() external view returns (uint8)',
  'function description() external view returns (string)',
];

// Chainlink price feeds (Ethereum Mainnet)
export const CHAINLINK_FEEDS = {
  ETH_USD: '0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419',
  BTC_USD: '0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c',
  USDC_USD: '0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6',
  DAI_USD: '0xAed0c38402a5d19df6E4c03F4E2DceD6e29c1ee9',
  LINK_USD: '0x2c1d072e956AFFC0D435Cb7AC38EF18d24d9127c',
};

// Get Chainlink price
export function useChainlinkPrice(feedAddress: string) {
  const { data: priceData, isLoading: priceLoading } = useReadContract({
    address: feedAddress as `0x${string}`,
    abi: CHAINLINK_PRICE_FEED_ABI,
    functionName: 'latestRoundData',
  });

  const { data: decimals, isLoading: decimalsLoading } = useReadContract({
    address: feedAddress as `0x${string}`,
    abi: CHAINLINK_PRICE_FEED_ABI,
    functionName: 'decimals',
  });

  const price = priceData ? (priceData as any)[1] : 0n;
  const dec = decimals as number || 8;

  return {
    price,
    decimals: dec,
    formatted: Number(price) / Math.pow(10, dec),
    timestamp: priceData ? (priceData as any)[3] : 0n,
    isLoading: priceLoading || decimalsLoading,
  };
}

// Get multiple prices
export async function getChainlinkPrices(
  provider: BrowserProvider,
  feeds: string[]
): Promise<Array<{ feed: string; price: bigint; decimals: number }>> {
  const results = await Promise.all(
    feeds.map(async (feed) => {
      const priceFeed = new Contract(feed, CHAINLINK_PRICE_FEED_ABI, provider);
      const [roundData, decimals] = await Promise.all([
        priceFeed.latestRoundData(),
        priceFeed.decimals(),
      ]);

      return {
        feed,
        price: roundData[1],
        decimals,
      };
    })
  );

  return results;
}

// Check if price is stale
export function isPriceStale(
  timestamp: bigint,
  maxAgeSeconds: number = 3600
): boolean {
  const now = BigInt(Math.floor(Date.now() / 1000));
  return now - timestamp > BigInt(maxAgeSeconds);
}

// Uniswap V2 TWAP Oracle
const UNISWAP_V2_PAIR_ABI = [
  'function price0CumulativeLast() external view returns (uint)',
  'function price1CumulativeLast() external view returns (uint)',
  'function getReserves() external view returns (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast)',
];

export async function getUniswapTWAP(
  provider: BrowserProvider,
  pairAddress: string,
  token0: boolean = true
): Promise<number> {
  const pair = new Contract(pairAddress, UNISWAP_V2_PAIR_ABI, provider);

  const [price0, price1, reserves] = await Promise.all([
    pair.price0CumulativeLast(),
    pair.price1CumulativeLast(),
    pair.getReserves(),
  ]);

  const price = token0 ? price0 : price1;
  const reserve0 = reserves[0];
  const reserve1 = reserves[1];

  return Number(reserve1) / Number(reserve0);
}

// Convert price between tokens
export function convertPrice(
  amount: bigint,
  priceInUSD: number,
  decimals: number = 18
): number {
  return (Number(amount) / Math.pow(10, decimals)) * priceInUSD;
}

export default {
  useChainlinkPrice,
  getChainlinkPrices,
  isPriceStale,
  getUniswapTWAP,
  convertPrice,
  CHAINLINK_FEEDS,
};
