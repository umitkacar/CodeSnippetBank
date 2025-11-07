/**
 * Synthetic Assets (Synthetix)
 * Mint and trade synthetic assets
 */

import { BrowserProvider, Contract } from 'ethers';
import { useWriteContract, useWaitForTransactionReceipt } from 'wagmi';

const SYNTHETIX_ABI = [
  'function mint() external',
  'function burn(uint amount) external',
  'function exchange(bytes32 sourceCurrencyKey, uint sourceAmount, bytes32 destinationCurrencyKey) external returns (uint amountReceived)',
  'function transferableSynthetix(address account) external view returns (uint)',
  'function collateralisationRatio(address account) external view returns (uint)',
];

// Mint sUSD by locking SNX
export function useSynthetixMint(synthetixAddress: string) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const mint = async () => {
    writeContract({
      address: synthetixAddress as `0x${string}`,
      abi: SYNTHETIX_ABI,
      functionName: 'mint',
    });
  };

  return {
    mint,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Burn sUSD to unlock SNX
export function useSynthetixBurn(synthetixAddress: string) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const burn = async (amount: bigint) => {
    writeContract({
      address: synthetixAddress as `0x${string}`,
      abi: SYNTHETIX_ABI,
      functionName: 'burn',
      args: [amount],
    });
  };

  return {
    burn,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Exchange synths
export function useSynthetixExchange(synthetixAddress: string) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const exchange = async (
    sourceCurrency: string,
    sourceAmount: bigint,
    destinationCurrency: string
  ) => {
    writeContract({
      address: synthetixAddress as `0x${string}`,
      abi: SYNTHETIX_ABI,
      functionName: 'exchange',
      args: [sourceCurrency, sourceAmount, destinationCurrency],
    });
  };

  return {
    exchange,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Get collateralization ratio
export async function getCollateralizationRatio(
  provider: BrowserProvider,
  synthetixAddress: string,
  userAddress: string
): Promise<number> {
  const synthetix = new Contract(synthetixAddress, SYNTHETIX_ABI, provider);
  const ratio = await synthetix.collateralisationRatio(userAddress);
  return Number(ratio) / 1e18;
}

export default {
  useSynthetixMint,
  useSynthetixBurn,
  useSynthetixExchange,
  getCollateralizationRatio,
};
