/**
 * DeFi Insurance (Nexus Mutual, InsurAce)
 * Smart contract and protocol insurance
 */

import { BrowserProvider, Contract } from 'ethers';
import { useWriteContract, useWaitForTransactionReceipt } from 'wagmi';

const INSURANCE_ABI = [
  'function buyCover(address contractAddress, bytes4 currency, uint256 amount, uint16 period, uint8 v, bytes32 r, bytes32 s) external payable',
  'function submitClaim(uint256 coverId) external',
  'function getCoverPrice(address contractAddress, bytes4 currency, uint256 amount, uint16 period) external view returns (uint256 price)',
];

// Buy insurance cover
export function useBuyInsurance(insuranceAddress: string) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const buyCover = async (
    contractAddress: string,
    amount: bigint,
    periodDays: number,
    price: bigint
  ) => {
    writeContract({
      address: insuranceAddress as `0x${string}`,
      abi: INSURANCE_ABI,
      functionName: 'buyCover',
      args: [
        contractAddress,
        '0x45544800', // ETH
        amount,
        periodDays,
        0, // v
        '0x0000000000000000000000000000000000000000000000000000000000000000', // r
        '0x0000000000000000000000000000000000000000000000000000000000000000', // s
      ],
      value: price,
    });
  };

  return {
    buyCover,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Submit claim
export function useSubmitClaim(insuranceAddress: string) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const submitClaim = async (coverId: bigint) => {
    writeContract({
      address: insuranceAddress as `0x${string}`,
      abi: INSURANCE_ABI,
      functionName: 'submitClaim',
      args: [coverId],
    });
  };

  return {
    submitClaim,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Get insurance quote
export async function getInsuranceQuote(
  provider: BrowserProvider,
  insuranceAddress: string,
  contractAddress: string,
  amount: bigint,
  periodDays: number
): Promise<bigint> {
  const insurance = new Contract(insuranceAddress, INSURANCE_ABI, provider);

  return await insurance.getCoverPrice(
    contractAddress,
    '0x45544800', // ETH
    amount,
    periodDays
  );
}

// Calculate premium percentage
export function calculatePremiumPercentage(
  coverAmount: bigint,
  premium: bigint
): number {
  return (Number(premium) / Number(coverAmount)) * 100;
}

export default {
  useBuyInsurance,
  useSubmitClaim,
  getInsuranceQuote,
  calculatePremiumPercentage,
};
