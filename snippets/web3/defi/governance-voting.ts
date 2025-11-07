/**
 * Governance and Voting
 * DAO governance token voting
 */

import { BrowserProvider, Contract } from 'ethers';
import { useWriteContract, useWaitForTransactionReceipt, useReadContract } from 'wagmi';

const GOVERNOR_ABI = [
  'function propose(address[] targets, uint256[] values, bytes[] calldatas, string description) external returns (uint256)',
  'function castVote(uint256 proposalId, uint8 support) external returns (uint256)',
  'function castVoteWithReason(uint256 proposalId, uint8 support, string reason) external returns (uint256)',
  'function execute(address[] targets, uint256[] values, bytes[] calldatas, bytes32 descriptionHash) external payable returns (uint256)',
  'function state(uint256 proposalId) external view returns (uint8)',
  'function proposalVotes(uint256 proposalId) external view returns (uint256 againstVotes, uint256 forVotes, uint256 abstainVotes)',
  'function hasVoted(uint256 proposalId, address account) external view returns (bool)',
  'function getVotes(address account, uint256 blockNumber) external view returns (uint256)',
];

export enum VoteType {
  Against = 0,
  For = 1,
  Abstain = 2,
}

export enum ProposalState {
  Pending = 0,
  Active = 1,
  Canceled = 2,
  Defeated = 3,
  Succeeded = 4,
  Queued = 5,
  Expired = 6,
  Executed = 7,
}

// Create proposal
export function useCreateProposal(governorAddress: string) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const propose = async (
    targets: string[],
    values: bigint[],
    calldatas: string[],
    description: string
  ) => {
    writeContract({
      address: governorAddress as `0x${string}`,
      abi: GOVERNOR_ABI,
      functionName: 'propose',
      args: [targets, values, calldatas, description],
    });
  };

  return {
    propose,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Cast vote
export function useCastVote(governorAddress: string) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const vote = async (proposalId: bigint, support: VoteType) => {
    writeContract({
      address: governorAddress as `0x${string}`,
      abi: GOVERNOR_ABI,
      functionName: 'castVote',
      args: [proposalId, support],
    });
  };

  const voteWithReason = async (
    proposalId: bigint,
    support: VoteType,
    reason: string
  ) => {
    writeContract({
      address: governorAddress as `0x${string}`,
      abi: GOVERNOR_ABI,
      functionName: 'castVoteWithReason',
      args: [proposalId, support, reason],
    });
  };

  return {
    vote,
    voteWithReason,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Execute proposal
export function useExecuteProposal(governorAddress: string) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const execute = async (
    targets: string[],
    values: bigint[],
    calldatas: string[],
    descriptionHash: string
  ) => {
    writeContract({
      address: governorAddress as `0x${string}`,
      abi: GOVERNOR_ABI,
      functionName: 'execute',
      args: [targets, values, calldatas, descriptionHash],
    });
  };

  return {
    execute,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Get proposal state
export function useProposalState(governorAddress: string, proposalId: bigint) {
  const { data, isLoading, refetch } = useReadContract({
    address: governorAddress as `0x${string}`,
    abi: GOVERNOR_ABI,
    functionName: 'state',
    args: [proposalId],
  });

  return {
    state: data as ProposalState,
    isLoading,
    refetch,
  };
}

// Get proposal votes
export async function getProposalVotes(
  provider: BrowserProvider,
  governorAddress: string,
  proposalId: bigint
): Promise<{ against: bigint; for: bigint; abstain: bigint }> {
  const governor = new Contract(governorAddress, GOVERNOR_ABI, provider);
  const votes = await governor.proposalVotes(proposalId);

  return {
    against: votes[0],
    for: votes[1],
    abstain: votes[2],
  };
}

// Check if user has voted
export async function hasUserVoted(
  provider: BrowserProvider,
  governorAddress: string,
  proposalId: bigint,
  userAddress: string
): Promise<boolean> {
  const governor = new Contract(governorAddress, GOVERNOR_ABI, provider);
  return await governor.hasVoted(proposalId, userAddress);
}

// Get voting power
export async function getVotingPower(
  provider: BrowserProvider,
  governorAddress: string,
  userAddress: string,
  blockNumber: number
): Promise<bigint> {
  const governor = new Contract(governorAddress, GOVERNOR_ABI, provider);
  return await governor.getVotes(userAddress, blockNumber);
}

export default {
  useCreateProposal,
  useCastVote,
  useExecuteProposal,
  useProposalState,
  getProposalVotes,
  hasUserVoted,
  getVotingPower,
  VoteType,
  ProposalState,
};
