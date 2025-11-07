/**
 * Contract Factory Pattern
 * Deploy and manage contract instances
 */

import { useWriteContract, useWaitForTransactionReceipt, useReadContract } from 'wagmi';
import { BrowserProvider, ContractFactory, Contract } from 'ethers';

// Deploy contract with ethers.js
export async function deployContract(
  provider: BrowserProvider,
  abi: any[],
  bytecode: string,
  args: any[] = []
): Promise<{ contract: Contract; address: string; deployTransaction: any }> {
  const signer = await provider.getSigner();
  const factory = new ContractFactory(abi, bytecode, signer);

  const contract = await factory.deploy(...args);
  await contract.waitForDeployment();

  const address = await contract.getAddress();

  return {
    contract,
    address,
    deployTransaction: contract.deploymentTransaction(),
  };
}

// Factory contract pattern
const FACTORY_ABI = [
  'function createContract(bytes32 salt, bytes memory bytecode) returns (address)',
  'function getDeployedContracts() view returns (address[])',
  'function isDeployed(address contractAddress) view returns (bool)',
];

// Use factory to create contracts
export function useContractFactory(factoryAddress: string) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const createContract = async (salt: string, bytecode: string) => {
    writeContract({
      address: factoryAddress as `0x${string}`,
      abi: FACTORY_ABI,
      functionName: 'createContract',
      args: [salt, bytecode],
    });
  };

  return {
    createContract,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Get deployed contracts from factory
export function useDeployedContracts(factoryAddress: string) {
  const { data, isLoading, refetch } = useReadContract({
    address: factoryAddress as `0x${string}`,
    abi: FACTORY_ABI,
    functionName: 'getDeployedContracts',
  });

  return {
    contracts: data as string[],
    isLoading,
    refetch,
  };
}

// Clone factory pattern (EIP-1167)
export const CLONE_FACTORY_ABI = [
  'function clone(address implementation) returns (address)',
  'function cloneDeterministic(address implementation, bytes32 salt) returns (address)',
  'function predictDeterministicAddress(address implementation, bytes32 salt) view returns (address)',
];

// Deploy minimal proxy clone
export function useCloneFactory(factoryAddress: string) {
  const { writeContract, data: hash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const clone = async (implementationAddress: string) => {
    writeContract({
      address: factoryAddress as `0x${string}`,
      abi: CLONE_FACTORY_ABI,
      functionName: 'clone',
      args: [implementationAddress],
    });
  };

  const cloneDeterministic = async (implementationAddress: string, salt: string) => {
    writeContract({
      address: factoryAddress as `0x${string}`,
      abi: CLONE_FACTORY_ABI,
      functionName: 'cloneDeterministic',
      args: [implementationAddress, salt],
    });
  };

  return {
    clone,
    cloneDeterministic,
    hash,
    isPending,
    isConfirming,
    isSuccess,
  };
}

// Predict clone address
export function usePredictCloneAddress(
  factoryAddress: string,
  implementationAddress: string,
  salt: string
) {
  const { data: predictedAddress, isLoading } = useReadContract({
    address: factoryAddress as `0x${string}`,
    abi: CLONE_FACTORY_ABI,
    functionName: 'predictDeterministicAddress',
    args: [implementationAddress, salt],
  });

  return {
    predictedAddress: predictedAddress as string,
    isLoading,
  };
}

// CREATE2 deployment
export async function deployWithCreate2(
  provider: BrowserProvider,
  factoryAddress: string,
  bytecode: string,
  salt: string
): Promise<string> {
  const signer = await provider.getSigner();
  const factory = new Contract(factoryAddress, FACTORY_ABI, signer);

  const tx = await factory.createContract(salt, bytecode);
  const receipt = await tx.wait();

  // Extract deployed address from events
  const event = receipt.logs.find((log: any) => log.eventName === 'ContractCreated');
  return event?.args?.contractAddress;
}

export default {
  deployContract,
  useContractFactory,
  useDeployedContracts,
  useCloneFactory,
  usePredictCloneAddress,
  deployWithCreate2,
};
