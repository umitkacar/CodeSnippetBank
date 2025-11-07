/**
 * Signature Verification and Message Signing
 * EIP-191 and EIP-712 typed data signing
 */

import { useSignMessage, useSignTypedData } from 'wagmi';
import { BrowserProvider } from 'ethers';
import { verifyMessage, verifyTypedData } from 'ethers';

// Sign simple message
export function useMessageSigning() {
  const { data: signature, signMessage, isPending, error } = useSignMessage();

  const sign = async (message: string) => {
    await signMessage({ message });
  };

  return {
    signature,
    sign,
    isPending,
    error,
  };
}

// Sign typed data (EIP-712)
export function useTypedDataSigning() {
  const { data: signature, signTypedData, isPending, error } = useSignTypedData();

  const sign = async (domain: any, types: any, value: any) => {
    await signTypedData({
      domain,
      types,
      primaryType: Object.keys(types)[0],
      message: value,
    });
  };

  return {
    signature,
    sign,
    isPending,
    error,
  };
}

// Sign message with ethers.js
export async function signMessageWithEthers(
  provider: BrowserProvider,
  message: string
): Promise<string> {
  const signer = await provider.getSigner();
  return await signer.signMessage(message);
}

// Verify message signature
export async function verifyMessageSignature(
  message: string,
  signature: string
): Promise<string> {
  return verifyMessage(message, signature);
}

// EIP-712 typed data example
export const EIP712_DOMAIN = {
  name: 'My DApp',
  version: '1',
  chainId: 1,
  verifyingContract: '0x0000000000000000000000000000000000000000' as `0x${string}`,
};

export const EIP712_TYPES = {
  Mail: [
    { name: 'from', type: 'address' },
    { name: 'to', type: 'address' },
    { name: 'contents', type: 'string' },
  ],
};

// Sign EIP-712 typed data
export async function signTypedDataWithEthers(
  provider: BrowserProvider,
  domain: any,
  types: any,
  value: any
): Promise<string> {
  const signer = await provider.getSigner();
  return await signer.signTypedData(domain, types, value);
}

// Verify EIP-712 signature
export async function verifyTypedDataSignature(
  domain: any,
  types: any,
  value: any,
  signature: string
): Promise<string> {
  return verifyTypedData(domain, types, value, signature);
}

// Login with Ethereum (SIWE - Sign-In with Ethereum)
export const createSiweMessage = (
  address: string,
  statement: string,
  nonce: string,
  domain: string
) => {
  const message = `${domain} wants you to sign in with your Ethereum account:
${address}

${statement}

URI: https://${domain}
Version: 1
Chain ID: 1
Nonce: ${nonce}
Issued At: ${new Date().toISOString()}`;

  return message;
};

// Permit signature (EIP-2612)
export const PERMIT_TYPES = {
  Permit: [
    { name: 'owner', type: 'address' },
    { name: 'spender', type: 'address' },
    { name: 'value', type: 'uint256' },
    { name: 'nonce', type: 'uint256' },
    { name: 'deadline', type: 'uint256' },
  ],
};

// Create permit signature
export async function createPermitSignature(
  provider: BrowserProvider,
  tokenAddress: string,
  owner: string,
  spender: string,
  value: bigint,
  nonce: number,
  deadline: number,
  chainId: number
) {
  const domain = {
    name: 'Token Name',
    version: '1',
    chainId,
    verifyingContract: tokenAddress as `0x${string}`,
  };

  const message = {
    owner,
    spender,
    value,
    nonce,
    deadline,
  };

  const signer = await provider.getSigner();
  return await signer.signTypedData(domain, PERMIT_TYPES, message);
}

// Signature recovery
export function recoverSigner(message: string, signature: string): string {
  return verifyMessage(message, signature);
}

export default {
  useMessageSigning,
  useTypedDataSigning,
  signMessageWithEthers,
  verifyMessageSignature,
  signTypedDataWithEthers,
  verifyTypedDataSignature,
  createSiweMessage,
  createPermitSignature,
  recoverSigner,
  EIP712_DOMAIN,
  EIP712_TYPES,
  PERMIT_TYPES,
};
