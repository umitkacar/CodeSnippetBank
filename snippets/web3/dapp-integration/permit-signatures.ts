/**
 * EIP-2612 Permit Signatures
 * Gasless token approvals using permit
 */

import { useSignTypedData } from 'wagmi';
import { BrowserProvider, Contract } from 'ethers';
import { useState } from 'react';

const ERC20_PERMIT_ABI = [
  'function permit(address owner, address spender, uint256 value, uint256 deadline, uint8 v, bytes32 r, bytes32 s)',
  'function nonces(address owner) view returns (uint256)',
  'function DOMAIN_SEPARATOR() view returns (bytes32)',
];

// Permit types for EIP-712
export const PERMIT_TYPES = {
  Permit: [
    { name: 'owner', type: 'address' },
    { name: 'spender', type: 'address' },
    { name: 'value', type: 'uint256' },
    { name: 'nonce', type: 'uint256' },
    { name: 'deadline', type: 'uint256' },
  ],
};

// Sign permit
export function usePermitSignature() {
  const { signTypedData, data: signature, isPending } = useSignTypedData();

  const signPermit = async (
    tokenAddress: string,
    tokenName: string,
    owner: string,
    spender: string,
    value: bigint,
    nonce: number,
    deadline: number,
    chainId: number
  ) => {
    const domain = {
      name: tokenName,
      version: '1',
      chainId,
      verifyingContract: tokenAddress as `0x${string}`,
    };

    const message = {
      owner,
      spender,
      value: value.toString(),
      nonce,
      deadline,
    };

    await signTypedData({
      domain,
      types: PERMIT_TYPES,
      primaryType: 'Permit',
      message,
    });
  };

  return {
    signPermit,
    signature,
    isPending,
  };
}

// Get current nonce for permit
export async function getPermitNonce(
  provider: BrowserProvider,
  tokenAddress: string,
  owner: string
): Promise<number> {
  const contract = new Contract(tokenAddress, ERC20_PERMIT_ABI, provider);
  const nonce = await contract.nonces(owner);
  return Number(nonce);
}

// Execute permit
export async function executePermit(
  provider: BrowserProvider,
  tokenAddress: string,
  owner: string,
  spender: string,
  value: bigint,
  deadline: number,
  signature: `0x${string}`
): Promise<any> {
  const signer = await provider.getSigner();
  const contract = new Contract(tokenAddress, ERC20_PERMIT_ABI, signer);

  // Split signature
  const r = signature.slice(0, 66);
  const s = `0x${signature.slice(66, 130)}`;
  const v = parseInt(signature.slice(130, 132), 16);

  const tx = await contract.permit(owner, spender, value, deadline, v, r, s);
  return await tx.wait();
}

// Complete permit flow
export function usePermitApproval(tokenAddress: string, tokenName: string) {
  const { signPermit, signature, isPending } = usePermitSignature();
  const [isExecuting, setIsExecuting] = useState(false);

  const approveWithPermit = async (
    provider: BrowserProvider,
    owner: string,
    spender: string,
    value: bigint,
    chainId: number
  ) => {
    // Get current nonce
    const nonce = await getPermitNonce(provider, tokenAddress, owner);

    // Set deadline (1 hour from now)
    const deadline = Math.floor(Date.now() / 1000) + 3600;

    // Sign permit
    await signPermit(
      tokenAddress,
      tokenName,
      owner,
      spender,
      value,
      nonce,
      deadline,
      chainId
    );

    if (!signature) {
      throw new Error('Failed to get signature');
    }

    // Execute permit
    setIsExecuting(true);
    try {
      const receipt = await executePermit(
        provider,
        tokenAddress,
        owner,
        spender,
        value,
        deadline,
        signature
      );
      return receipt;
    } finally {
      setIsExecuting(false);
    }
  };

  return {
    approveWithPermit,
    signature,
    isPending: isPending || isExecuting,
  };
}

// DAI-style permit (different signature format)
export const DAI_PERMIT_TYPES = {
  Permit: [
    { name: 'holder', type: 'address' },
    { name: 'spender', type: 'address' },
    { name: 'nonce', type: 'uint256' },
    { name: 'expiry', type: 'uint256' },
    { name: 'allowed', type: 'bool' },
  ],
};

// Sign DAI permit
export async function signDaiPermit(
  provider: BrowserProvider,
  tokenAddress: string,
  holder: string,
  spender: string,
  nonce: number,
  expiry: number,
  chainId: number
): Promise<{ v: number; r: string; s: string }> {
  const domain = {
    name: 'Dai Stablecoin',
    version: '1',
    chainId,
    verifyingContract: tokenAddress as `0x${string}`,
  };

  const message = {
    holder,
    spender,
    nonce,
    expiry,
    allowed: true,
  };

  const signer = await provider.getSigner();
  const signature = await signer.signTypedData(domain, DAI_PERMIT_TYPES, message);

  const r = signature.slice(0, 66);
  const s = `0x${signature.slice(66, 130)}`;
  const v = parseInt(signature.slice(130, 132), 16);

  return { v, r, s };
}

// Batch permit for multiple tokens
export async function batchPermitSignatures(
  provider: BrowserProvider,
  permits: Array<{
    tokenAddress: string;
    tokenName: string;
    spender: string;
    value: bigint;
  }>,
  owner: string,
  chainId: number
): Promise<
  Array<{
    tokenAddress: string;
    signature: string;
    deadline: number;
    nonce: number;
  }>
> {
  const deadline = Math.floor(Date.now() / 1000) + 3600;

  const results = await Promise.all(
    permits.map(async (permit) => {
      const nonce = await getPermitNonce(provider, permit.tokenAddress, owner);

      const domain = {
        name: permit.tokenName,
        version: '1',
        chainId,
        verifyingContract: permit.tokenAddress as `0x${string}`,
      };

      const message = {
        owner,
        spender: permit.spender,
        value: permit.value.toString(),
        nonce,
        deadline,
      };

      const signer = await provider.getSigner();
      const signature = await signer.signTypedData(domain, PERMIT_TYPES, message);

      return {
        tokenAddress: permit.tokenAddress,
        signature,
        deadline,
        nonce,
      };
    })
  );

  return results;
}

export default {
  usePermitSignature,
  getPermitNonce,
  executePermit,
  usePermitApproval,
  signDaiPermit,
  batchPermitSignatures,
  PERMIT_TYPES,
  DAI_PERMIT_TYPES,
};
