/**
 * Token Swap Aggregator
 * 1inch and other DEX aggregators
 */

import axios from 'axios';

const ONEINCH_API_BASE = 'https://api.1inch.io/v5.0';

export interface SwapQuote {
  fromToken: string;
  toToken: string;
  fromAmount: string;
  toAmount: string;
  protocols: any[];
  estimatedGas: number;
}

// Get 1inch swap quote
export async function get1inchQuote(
  chainId: number,
  fromToken: string,
  toToken: string,
  amount: string
): Promise<SwapQuote> {
  const response = await axios.get(
    `${ONEINCH_API_BASE}/${chainId}/quote`,
    {
      params: {
        fromTokenAddress: fromToken,
        toTokenAddress: toToken,
        amount,
      },
    }
  );

  return {
    fromToken: response.data.fromToken.address,
    toToken: response.data.toToken.address,
    fromAmount: response.data.fromTokenAmount,
    toAmount: response.data.toTokenAmount,
    protocols: response.data.protocols,
    estimatedGas: response.data.estimatedGas,
  };
}

// Get 1inch swap transaction
export async function get1inchSwapTx(
  chainId: number,
  fromToken: string,
  toToken: string,
  amount: string,
  fromAddress: string,
  slippage: number = 1
): Promise<{ to: string; data: string; value: string }> {
  const response = await axios.get(
    `${ONEINCH_API_BASE}/${chainId}/swap`,
    {
      params: {
        fromTokenAddress: fromToken,
        toTokenAddress: toToken,
        amount,
        fromAddress,
        slippage,
      },
    }
  );

  return {
    to: response.data.tx.to,
    data: response.data.tx.data,
    value: response.data.tx.value,
  };
}

// Get supported tokens
export async function get1inchTokens(
  chainId: number
): Promise<Record<string, any>> {
  const response = await axios.get(
    `${ONEINCH_API_BASE}/${chainId}/tokens`
  );

  return response.data.tokens;
}

// Compare prices across DEXes
export interface DEXPrice {
  dex: string;
  price: number;
  amountOut: bigint;
}

export async function compareDEXPrices(
  chainId: number,
  fromToken: string,
  toToken: string,
  amount: string
): Promise<DEXPrice[]> {
  // Get 1inch quote which includes all DEXes
  const quote = await get1inchQuote(chainId, fromToken, toToken, amount);

  return quote.protocols.map((protocol: any) => ({
    dex: protocol[0][0].name,
    price: Number(quote.toAmount) / Number(quote.fromAmount),
    amountOut: BigInt(quote.toAmount),
  }));
}

// Find best price
export function findBestPrice(prices: DEXPrice[]): DEXPrice {
  return prices.reduce((best, current) =>
    current.amountOut > best.amountOut ? current : best
  );
}

// Calculate savings
export function calculateSavings(
  aggregatorPrice: bigint,
  dexPrice: bigint
): { savings: bigint; percentage: number } {
  const savings = aggregatorPrice - dexPrice;
  const percentage = Number((savings * 10000n) / dexPrice) / 100;

  return { savings, percentage };
}

export default {
  get1inchQuote,
  get1inchSwapTx,
  get1inchTokens,
  compareDEXPrices,
  findBestPrice,
  calculateSavings,
};
