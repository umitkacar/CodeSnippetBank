/**
 * ENS (Ethereum Name Service) Resolution
 * Resolve ENS names to addresses and vice versa
 */

import { useEnsName, useEnsAddress, useEnsAvatar } from 'wagmi';
import { BrowserProvider } from 'ethers';
import { normalize } from 'viem/ens';

// Resolve ENS name to address
export function useResolveEnsName(ensName: string) {
  const { data: address, isLoading, isError } = useEnsAddress({
    name: normalize(ensName),
    chainId: 1, // Mainnet
  });

  return {
    address,
    isLoading,
    isError,
  };
}

// Resolve address to ENS name
export function useResolveAddress(address: string) {
  const { data: ensName, isLoading, isError } = useEnsName({
    address: address as `0x${string}`,
    chainId: 1,
  });

  return {
    ensName,
    isLoading,
    isError,
  };
}

// Get ENS avatar
export function useEnsAvatarUrl(ensName: string) {
  const { data: avatar, isLoading, isError } = useEnsAvatar({
    name: normalize(ensName),
    chainId: 1,
  });

  return {
    avatar,
    isLoading,
    isError,
  };
}

// Complete ENS profile
export function useEnsProfile(address: string) {
  const { ensName } = useResolveAddress(address);
  const { avatar } = useEnsAvatarUrl(ensName || '');

  return {
    address,
    ensName,
    avatar,
  };
}

// ENS resolution with ethers.js
export async function resolveEnsWithEthers(
  provider: BrowserProvider,
  ensName: string
): Promise<string | null> {
  try {
    return await provider.resolveName(ensName);
  } catch (error) {
    console.error('ENS resolution failed:', error);
    return null;
  }
}

// Reverse ENS lookup with ethers.js
export async function reverseEnsLookup(
  provider: BrowserProvider,
  address: string
): Promise<string | null> {
  try {
    return await provider.lookupAddress(address);
  } catch (error) {
    console.error('Reverse ENS lookup failed:', error);
    return null;
  }
}

// Batch ENS resolution
export async function batchResolveEns(
  provider: BrowserProvider,
  ensNames: string[]
): Promise<Array<{ name: string; address: string | null }>> {
  const results = await Promise.all(
    ensNames.map(async (name) => ({
      name,
      address: await resolveEnsWithEthers(provider, name),
    }))
  );

  return results;
}

// Display name helper (ENS or shortened address)
export function useDisplayName(address: string) {
  const { ensName } = useResolveAddress(address);

  const displayName = ensName || `${address.slice(0, 6)}...${address.slice(-4)}`;

  return displayName;
}

// ENS availability check
export async function checkEnsAvailability(
  provider: BrowserProvider,
  ensName: string
): Promise<boolean> {
  const address = await provider.resolveName(ensName);
  return address === null;
}

// ENS component
export function EnsDisplay({ address }: { address: string }) {
  const displayName = useDisplayName(address);
  const { avatar } = useEnsProfile(address);

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      {avatar && (
        <img
          src={avatar}
          alt={displayName}
          style={{ width: '32px', height: '32px', borderRadius: '50%' }}
        />
      )}
      <span>{displayName}</span>
    </div>
  );
}

export default {
  useResolveEnsName,
  useResolveAddress,
  useEnsAvatarUrl,
  useEnsProfile,
  resolveEnsWithEthers,
  reverseEnsLookup,
  batchResolveEns,
  useDisplayName,
  checkEnsAvailability,
  EnsDisplay,
};
