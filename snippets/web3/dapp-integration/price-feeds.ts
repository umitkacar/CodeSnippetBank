/**
 * Token Price Feeds
 * Fetch token prices from various sources
 */

import { useState, useEffect } from 'react';

// CoinGecko price feed
export async function fetchCoinGeckoPrice(
  tokenAddress: string,
  currency: string = 'usd'
): Promise<number> {
  const response = await fetch(
    `https://api.coingecko.com/api/v3/simple/token_price/ethereum?contract_addresses=${tokenAddress}&vs_currencies=${currency}`
  );

  const data = await response.json();
  return data[tokenAddress.toLowerCase()]?.[currency] || 0;
}

// CoinGecko batch prices
export async function fetchCoinGeckoBatchPrices(
  tokenAddresses: string[],
  currency: string = 'usd'
): Promise<Record<string, number>> {
  const addresses = tokenAddresses.join(',');
  const response = await fetch(
    `https://api.coingecko.com/api/v3/simple/token_price/ethereum?contract_addresses=${addresses}&vs_currencies=${currency}`
  );

  const data = await response.json();
  const prices: Record<string, number> = {};

  tokenAddresses.forEach((address) => {
    prices[address.toLowerCase()] = data[address.toLowerCase()]?.[currency] || 0;
  });

  return prices;
}

// Hook for real-time price
export function useTokenPrice(
  tokenAddress: string,
  currency: string = 'usd',
  refreshInterval: number = 60000 // 1 minute
) {
  const [price, setPrice] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchPrice = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const fetchedPrice = await fetchCoinGeckoPrice(tokenAddress, currency);
        setPrice(fetchedPrice);
      } catch (err) {
        setError(err as Error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPrice();
    const interval = setInterval(fetchPrice, refreshInterval);

    return () => clearInterval(interval);
  }, [tokenAddress, currency, refreshInterval]);

  return { price, isLoading, error };
}

// Hook for multiple token prices
export function useTokenPrices(
  tokenAddresses: string[],
  currency: string = 'usd',
  refreshInterval: number = 60000
) {
  const [prices, setPrices] = useState<Record<string, number>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchPrices = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const fetchedPrices = await fetchCoinGeckoBatchPrices(
          tokenAddresses,
          currency
        );
        setPrices(fetchedPrices);
      } catch (err) {
        setError(err as Error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPrices();
    const interval = setInterval(fetchPrices, refreshInterval);

    return () => clearInterval(interval);
  }, [tokenAddresses.join(','), currency, refreshInterval]);

  return { prices, isLoading, error };
}

// 1inch price feed
export async function fetch1inchPrice(
  chainId: number,
  tokenAddress: string
): Promise<number> {
  const response = await fetch(
    `https://api.1inch.io/v5.0/${chainId}/quote?fromTokenAddress=${tokenAddress}&toTokenAddress=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE&amount=1000000000000000000`
  );

  const data = await response.json();
  return parseFloat(data.toTokenAmount) / 1e18;
}

// Uniswap price from pool
export async function fetchUniswapV3Price(
  poolAddress: string,
  tokenAddress: string,
  provider: any
): Promise<number> {
  const POOL_ABI = [
    'function slot0() view returns (uint160 sqrtPriceX96, int24 tick, uint16 observationIndex, uint16 observationCardinality, uint16 observationCardinalityNext, uint8 feeProtocol, bool unlocked)',
    'function token0() view returns (address)',
    'function token1() view returns (address)',
  ];

  const Contract = (await import('ethers')).Contract;
  const pool = new Contract(poolAddress, POOL_ABI, provider);

  const [sqrtPriceX96] = await pool.slot0();
  const token0 = await pool.token0();

  // Calculate price from sqrtPriceX96
  const price = (Number(sqrtPriceX96) / 2 ** 96) ** 2;

  // If token is token1, invert the price
  return tokenAddress.toLowerCase() === token0.toLowerCase() ? price : 1 / price;
}

// Price change percentage
export function calculatePriceChange(
  currentPrice: number,
  previousPrice: number
): { change: number; percentage: string } {
  const change = currentPrice - previousPrice;
  const percentage = ((change / previousPrice) * 100).toFixed(2);

  return { change, percentage };
}

// Format price for display
export function formatPrice(price: number, decimals: number = 2): string {
  if (price === 0) return '$0.00';
  if (price < 0.01) return `$${price.toFixed(6)}`;
  if (price < 1) return `$${price.toFixed(4)}`;

  return `$${price.toFixed(decimals)}`;
}

// Price display component
export function PriceDisplay({
  tokenAddress,
  showChange = false,
}: {
  tokenAddress: string;
  showChange?: boolean;
}) {
  const { price, isLoading } = useTokenPrice(tokenAddress);
  const [previousPrice, setPreviousPrice] = useState(price);

  useEffect(() => {
    if (price !== previousPrice && !isLoading) {
      setTimeout(() => setPreviousPrice(price), 60000);
    }
  }, [price, isLoading]);

  if (isLoading) return <span>Loading...</span>;

  const { change, percentage } = calculatePriceChange(price, previousPrice);
  const isPositive = change >= 0;

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <span>{formatPrice(price)}</span>
      {showChange && previousPrice !== price && (
        <span style={{ color: isPositive ? '#10b981' : '#ef4444' }}>
          {isPositive ? '+' : ''}
          {percentage}%
        </span>
      )}
    </div>
  );
}

// Historical price data
export async function fetchHistoricalPrices(
  tokenAddress: string,
  days: number = 7
): Promise<Array<{ timestamp: number; price: number }>> {
  const response = await fetch(
    `https://api.coingecko.com/api/v3/coins/ethereum/contract/${tokenAddress}/market_chart/?vs_currency=usd&days=${days}`
  );

  const data = await response.json();

  return data.prices.map(([timestamp, price]: [number, number]) => ({
    timestamp,
    price,
  }));
}

export default {
  fetchCoinGeckoPrice,
  fetchCoinGeckoBatchPrices,
  useTokenPrice,
  useTokenPrices,
  fetch1inchPrice,
  fetchUniswapV3Price,
  calculatePriceChange,
  formatPrice,
  PriceDisplay,
  fetchHistoricalPrices,
};
