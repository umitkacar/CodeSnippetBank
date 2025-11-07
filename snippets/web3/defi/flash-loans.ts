/**
 * Flash Loans
 * Execute flash loans on Aave and other protocols
 */

import { BrowserProvider, Contract } from 'ethers';

const AAVE_POOL_ABI = [
  'function flashLoan(address receiverAddress, address[] calldata assets, uint256[] calldata amounts, uint256[] calldata interestRateModes, address onBehalfOf, bytes calldata params, uint16 referralCode) external',
  'function FLASHLOAN_PREMIUM_TOTAL() external view returns (uint128)',
];

const FLASH_LOAN_RECEIVER_ABI = [
  'function executeOperation(address[] calldata assets, uint256[] calldata amounts, uint256[] calldata premiums, address initiator, bytes calldata params) external returns (bool)',
];

const AAVE_V3_POOL = '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2';

export interface FlashLoanParams {
  assets: string[];
  amounts: bigint[];
  receiverAddress: string;
  params: string;
}

// Execute flash loan
export async function executeFlashLoan(
  provider: BrowserProvider,
  params: FlashLoanParams
): Promise<any> {
  const signer = await provider.getSigner();
  const pool = new Contract(AAVE_V3_POOL, AAVE_POOL_ABI, signer);

  const interestRateModes = params.assets.map(() => 0); // 0 = no debt

  const tx = await pool.flashLoan(
    params.receiverAddress,
    params.assets,
    params.amounts,
    interestRateModes,
    await signer.getAddress(),
    params.params,
    0
  );

  return await tx.wait();
}

// Get flash loan premium
export async function getFlashLoanPremium(
  provider: BrowserProvider
): Promise<bigint> {
  const pool = new Contract(AAVE_V3_POOL, AAVE_POOL_ABI, provider);
  return await pool.FLASHLOAN_PREMIUM_TOTAL();
}

// Calculate flash loan fee
export function calculateFlashLoanFee(
  amount: bigint,
  premiumBps: bigint
): bigint {
  return (amount * premiumBps) / 10000n;
}

// Flash loan arbitrage example
export async function flashLoanArbitrage(
  provider: BrowserProvider,
  receiverAddress: string,
  token: string,
  amount: bigint,
  dex1Address: string,
  dex2Address: string
): Promise<any> {
  // Encode arbitrage parameters
  const params = new (require('ethers')).AbiCoder().encode(
    ['address', 'address', 'uint256'],
    [dex1Address, dex2Address, amount]
  );

  return executeFlashLoan(provider, {
    assets: [token],
    amounts: [amount],
    receiverAddress,
    params,
  });
}

// Uniswap flash swap
const UNISWAP_V2_PAIR_ABI = [
  'function swap(uint amount0Out, uint amount1Out, address to, bytes calldata data) external',
];

export async function executeUniswapFlashSwap(
  provider: BrowserProvider,
  pairAddress: string,
  amount0Out: bigint,
  amount1Out: bigint,
  receiverAddress: string,
  data: string
): Promise<any> {
  const signer = await provider.getSigner();
  const pair = new Contract(pairAddress, UNISWAP_V2_PAIR_ABI, signer);

  const tx = await pair.swap(amount0Out, amount1Out, receiverAddress, data);
  return await tx.wait();
}

export default {
  executeFlashLoan,
  getFlashLoanPremium,
  calculateFlashLoanFee,
  flashLoanArbitrage,
  executeUniswapFlashSwap,
  AAVE_V3_POOL,
};
