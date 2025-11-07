/**
 * Options Trading (DeFi)
 * Trade options on decentralized protocols
 */

import { BrowserProvider, Contract } from 'ethers';

const OPTIONS_ABI = [
  'function buyOption(uint256 optionId, uint256 amount) external payable',
  'function sellOption(uint256 optionId, uint256 amount) external',
  'function exerciseOption(uint256 optionId) external',
  'function getOptionPrice(uint256 optionId) external view returns (uint256)',
];

export interface Option {
  id: bigint;
  strike: bigint;
  expiry: number;
  isCall: boolean;
  premium: bigint;
}

// Calculate option intrinsic value
export function calculateIntrinsicValue(
  spotPrice: number,
  strikePrice: number,
  isCall: boolean
): number {
  if (isCall) {
    return Math.max(0, spotPrice - strikePrice);
  } else {
    return Math.max(0, strikePrice - spotPrice);
  }
}

// Black-Scholes option pricing
export function blackScholes(
  spotPrice: number,
  strikePrice: number,
  timeToExpiry: number,
  riskFreeRate: number,
  volatility: number,
  isCall: boolean
): number {
  const d1 =
    (Math.log(spotPrice / strikePrice) +
      (riskFreeRate + (volatility ** 2) / 2) * timeToExpiry) /
    (volatility * Math.sqrt(timeToExpiry));

  const d2 = d1 - volatility * Math.sqrt(timeToExpiry);

  const cumulativeNormal = (x: number) => {
    return (1 + erf(x / Math.sqrt(2))) / 2;
  };

  if (isCall) {
    return (
      spotPrice * cumulativeNormal(d1) -
      strikePrice *
        Math.exp(-riskFreeRate * timeToExpiry) *
        cumulativeNormal(d2)
    );
  } else {
    return (
      strikePrice *
        Math.exp(-riskFreeRate * timeToExpiry) *
        cumulativeNormal(-d2) -
      spotPrice * cumulativeNormal(-d1)
    );
  }
}

function erf(x: number): number {
  const sign = x >= 0 ? 1 : -1;
  x = Math.abs(x);

  const a1 = 0.254829592;
  const a2 = -0.284496736;
  const a3 = 1.421413741;
  const a4 = -1.453152027;
  const a5 = 1.061405429;
  const p = 0.3275911;

  const t = 1.0 / (1.0 + p * x);
  const y =
    1.0 - ((((a5 * t + a4) * t + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);

  return sign * y;
}

// Calculate option Greeks
export interface Greeks {
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  rho: number;
}

export function calculateGreeks(
  spotPrice: number,
  strikePrice: number,
  timeToExpiry: number,
  riskFreeRate: number,
  volatility: number,
  isCall: boolean
): Greeks {
  const d1 =
    (Math.log(spotPrice / strikePrice) +
      (riskFreeRate + (volatility ** 2) / 2) * timeToExpiry) /
    (volatility * Math.sqrt(timeToExpiry));

  const d2 = d1 - volatility * Math.sqrt(timeToExpiry);

  const cumulativeNormal = (x: number) => (1 + erf(x / Math.sqrt(2))) / 2;
  const normalDensity = (x: number) =>
    Math.exp(-(x ** 2) / 2) / Math.sqrt(2 * Math.PI);

  const delta = isCall ? cumulativeNormal(d1) : cumulativeNormal(d1) - 1;

  const gamma =
    normalDensity(d1) / (spotPrice * volatility * Math.sqrt(timeToExpiry));

  const theta = isCall
    ? (-spotPrice * normalDensity(d1) * volatility) /
        (2 * Math.sqrt(timeToExpiry)) -
      riskFreeRate *
        strikePrice *
        Math.exp(-riskFreeRate * timeToExpiry) *
        cumulativeNormal(d2)
    : (-spotPrice * normalDensity(d1) * volatility) /
        (2 * Math.sqrt(timeToExpiry)) +
      riskFreeRate *
        strikePrice *
        Math.exp(-riskFreeRate * timeToExpiry) *
        cumulativeNormal(-d2);

  const vega =
    (spotPrice * normalDensity(d1) * Math.sqrt(timeToExpiry)) / 100;

  const rho = isCall
    ? (strikePrice *
        timeToExpiry *
        Math.exp(-riskFreeRate * timeToExpiry) *
        cumulativeNormal(d2)) /
      100
    : (-strikePrice *
        timeToExpiry *
        Math.exp(-riskFreeRate * timeToExpiry) *
        cumulativeNormal(-d2)) /
      100;

  return { delta, gamma, theta, vega, rho };
}

export default {
  calculateIntrinsicValue,
  blackScholes,
  calculateGreeks,
};
