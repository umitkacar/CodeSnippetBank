/**
 * Cross-Chain Bridge
 * Transfer assets between blockchains
 */

import { BrowserProvider, Contract } from 'ethers';
import { useWriteContract, useWaitForTransactionReceipt } from 'wagmi';

const BRIDGE_ABI = [
  'function deposit(address token, uint256 amount, uint256 destinationChainId) external payable',
  'function withdraw(bytes32 depositHash, address token, uint256 amount, bytes signature) external',
  'function getFee(uint256 destinationChainId, uint256 amount) external view returns (uint256)',
];

// Bridge tokens to another chain
export function useBridgeDeposit(bridgeAddress: string) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const bridge = async (
    token: string,
    amount: bigint,
    destinationChainId: number,
    fee: bigint
  ) => {
    writeContract({
      address: bridgeAddress as `0x${string}`,
      abi: BRIDGE_ABI,
      functionName: 'deposit',
      args: [token, amount, destinationChainId],
      value: fee,
    });
  };

  return {
    bridge,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Get bridge fee
export async function getBridgeFee(
  provider: BrowserProvider,
  bridgeAddress: string,
  destinationChainId: number,
  amount: bigint
): Promise<bigint> {
  const bridge = new Contract(bridgeAddress, BRIDGE_ABI, provider);
  return await bridge.getFee(destinationChainId, amount);
}

// Popular bridge addresses
export const BRIDGES = {
  MULTICHAIN: '0x6ab6d61428fde76768d7b45d8bfeec19c6ef91a8',
  SYNAPSE: '0x2796317b0fF8538F253012862c06787Adfb8cEb6',
  STARGATE: '0x8731d54E9D02c286767d56ac03e8037C07e01e98',
};

// Calculate estimated time
export function estimateBridgeTime(
  sourceChain: number,
  destChain: number
): { min: number; max: number } {
  // Simplified estimation
  const baseTime = 5; // minutes

  if (sourceChain === 1 || destChain === 1) {
    // Ethereum mainnet
    return { min: baseTime, max: baseTime * 3 };
  }

  return { min: baseTime / 2, max: baseTime };
}

export default {
  useBridgeDeposit,
  getBridgeFee,
  estimateBridgeTime,
  BRIDGES,
};
