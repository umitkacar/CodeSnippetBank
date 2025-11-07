/**
 * Token Approval Management
 * Handle ERC20 approvals and allowances
 */

import { useReadContract, useWriteContract, useWaitForTransactionReceipt } from 'wagmi';
import { parseUnits, formatUnits, MaxUint256 } from 'ethers';

const ERC20_ABI = [
  'function approve(address spender, uint256 amount) returns (bool)',
  'function allowance(address owner, address spender) view returns (uint256)',
  'function increaseAllowance(address spender, uint256 addedValue) returns (bool)',
  'function decreaseAllowance(address spender, uint256 subtractedValue) returns (bool)',
];

// Check allowance
export function useAllowance(
  tokenAddress: string,
  owner: string,
  spender: string
) {
  const { data: allowance, isLoading, refetch } = useReadContract({
    address: tokenAddress as `0x${string}`,
    abi: ERC20_ABI,
    functionName: 'allowance',
    args: [owner, spender],
  });

  return {
    allowance: allowance as bigint,
    isLoading,
    refetch,
  };
}

// Approve tokens
export function useTokenApproval(tokenAddress: string) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const approve = async (
    spender: string,
    amount: string,
    decimals: number = 18
  ) => {
    const amountBN = parseUnits(amount, decimals);

    writeContract({
      address: tokenAddress as `0x${string}`,
      abi: ERC20_ABI,
      functionName: 'approve',
      args: [spender, amountBN],
    });
  };

  const approveMax = async (spender: string) => {
    writeContract({
      address: tokenAddress as `0x${string}`,
      abi: ERC20_ABI,
      functionName: 'approve',
      args: [spender, MaxUint256],
    });
  };

  return {
    approve,
    approveMax,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Check if approval is needed
export function useNeedsApproval(
  tokenAddress: string,
  owner: string,
  spender: string,
  requiredAmount: bigint
) {
  const { allowance, isLoading } = useAllowance(tokenAddress, owner, spender);

  const needsApproval = allowance ? allowance < requiredAmount : true;

  return {
    needsApproval,
    currentAllowance: allowance,
    isLoading,
  };
}

// Approval manager with auto-check
export function useApprovalManager(
  tokenAddress: string,
  spender: string,
  userAddress: string
) {
  const { allowance, refetch } = useAllowance(tokenAddress, userAddress, spender);
  const { approve, approveMax, hash, isPending, isConfirming, isSuccess } =
    useTokenApproval(tokenAddress);

  const checkAndApprove = async (amount: string, decimals: number = 18) => {
    const amountBN = parseUnits(amount, decimals);

    if (!allowance || allowance < amountBN) {
      await approve(spender, amount, decimals);
    }
  };

  const ensureAllowance = async (amount: string, decimals: number = 18) => {
    await refetch();
    const amountBN = parseUnits(amount, decimals);

    if (!allowance || allowance < amountBN) {
      throw new Error('Insufficient allowance');
    }
  };

  return {
    allowance,
    checkAndApprove,
    ensureAllowance,
    approve,
    approveMax,
    hash,
    isPending,
    isConfirming,
    isSuccess,
    refetch,
  };
}

// Multi-token approval
export function useMultiTokenApproval(
  tokens: Array<{ address: string; amount: string; decimals: number }>,
  spender: string,
  userAddress: string
) {
  const approvals = tokens.map((token) =>
    useAllowance(token.address, userAddress, spender)
  );

  const needsApprovals = approvals.map((approval, index) => {
    const requiredAmount = parseUnits(tokens[index].amount, tokens[index].decimals);
    return !approval.allowance || approval.allowance < requiredAmount;
  });

  const allApproved = needsApprovals.every((needs) => !needs);

  return {
    approvals,
    needsApprovals,
    allApproved,
  };
}

// Revoke approval
export function useRevokeApproval(tokenAddress: string) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const revoke = async (spender: string) => {
    writeContract({
      address: tokenAddress as `0x${string}`,
      abi: ERC20_ABI,
      functionName: 'approve',
      args: [spender, 0n],
    });
  };

  return {
    revoke,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

export default {
  useAllowance,
  useTokenApproval,
  useNeedsApproval,
  useApprovalManager,
  useMultiTokenApproval,
  useRevokeApproval,
};
