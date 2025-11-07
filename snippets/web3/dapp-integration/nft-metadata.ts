/**
 * NFT Metadata Utilities
 * Fetch and display NFT metadata
 */

import { useReadContract, useReadContracts } from 'wagmi';
import { useState, useEffect } from 'react';

const ERC721_ABI = [
  'function tokenURI(uint256 tokenId) view returns (string)',
  'function ownerOf(uint256 tokenId) view returns (address)',
  'function balanceOf(address owner) view returns (uint256)',
  'function name() view returns (string)',
  'function symbol() view returns (string)',
];

export interface NFTMetadata {
  name: string;
  description: string;
  image: string;
  attributes?: Array<{ trait_type: string; value: string | number }>;
  external_url?: string;
  background_color?: string;
  animation_url?: string;
}

// Fetch token URI
export function useTokenURI(contractAddress: string, tokenId: number) {
  const { data: tokenURI, isLoading } = useReadContract({
    address: contractAddress as `0x${string}`,
    abi: ERC721_ABI,
    functionName: 'tokenURI',
    args: [BigInt(tokenId)],
  });

  return {
    tokenURI: tokenURI as string,
    isLoading,
  };
}

// Fetch and parse NFT metadata
export function useNFTMetadata(contractAddress: string, tokenId: number) {
  const { tokenURI, isLoading: uriLoading } = useTokenURI(contractAddress, tokenId);
  const [metadata, setMetadata] = useState<NFTMetadata | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!tokenURI) return;

    const fetchMetadata = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // Handle IPFS URIs
        let url = tokenURI;
        if (tokenURI.startsWith('ipfs://')) {
          url = tokenURI.replace('ipfs://', 'https://ipfs.io/ipfs/');
        }

        const response = await fetch(url);
        const data = await response.json();

        // Convert IPFS image URLs
        if (data.image?.startsWith('ipfs://')) {
          data.image = data.image.replace('ipfs://', 'https://ipfs.io/ipfs/');
        }

        setMetadata(data);
      } catch (err) {
        setError(err as Error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMetadata();
  }, [tokenURI]);

  return {
    metadata,
    isLoading: uriLoading || isLoading,
    error,
  };
}

// Get NFT owner
export function useNFTOwner(contractAddress: string, tokenId: number) {
  const { data: owner, isLoading } = useReadContract({
    address: contractAddress as `0x${string}`,
    abi: ERC721_ABI,
    functionName: 'ownerOf',
    args: [BigInt(tokenId)],
  });

  return {
    owner: owner as string,
    isLoading,
  };
}

// Get collection info
export function useNFTCollection(contractAddress: string) {
  const { data } = useReadContracts({
    contracts: [
      {
        address: contractAddress as `0x${string}`,
        abi: ERC721_ABI,
        functionName: 'name',
      },
      {
        address: contractAddress as `0x${string}`,
        abi: ERC721_ABI,
        functionName: 'symbol',
      },
    ],
  });

  return {
    name: data?.[0]?.result as string,
    symbol: data?.[1]?.result as string,
  };
}

// Get user's NFT balance
export function useNFTBalance(contractAddress: string, userAddress: string) {
  const { data: balance, isLoading } = useReadContract({
    address: contractAddress as `0x${string}`,
    abi: ERC721_ABI,
    functionName: 'balanceOf',
    args: [userAddress],
  });

  return {
    balance: balance ? Number(balance) : 0,
    isLoading,
  };
}

// NFT card component
export function NFTCard({
  contractAddress,
  tokenId,
}: {
  contractAddress: string;
  tokenId: number;
}) {
  const { metadata, isLoading, error } = useNFTMetadata(contractAddress, tokenId);
  const { owner } = useNFTOwner(contractAddress, tokenId);

  if (isLoading) {
    return <div>Loading NFT...</div>;
  }

  if (error || !metadata) {
    return <div>Failed to load NFT metadata</div>;
  }

  return (
    <div
      style={{
        border: '1px solid #e5e7eb',
        borderRadius: '12px',
        padding: '16px',
        maxWidth: '300px',
      }}
    >
      <img
        src={metadata.image}
        alt={metadata.name}
        style={{ width: '100%', borderRadius: '8px' }}
      />
      <h3>{metadata.name}</h3>
      <p>{metadata.description}</p>
      {metadata.attributes && (
        <div>
          <h4>Attributes:</h4>
          {metadata.attributes.map((attr, index) => (
            <div key={index}>
              <strong>{attr.trait_type}:</strong> {attr.value}
            </div>
          ))}
        </div>
      )}
      <p style={{ fontSize: '12px', color: '#6b7280' }}>
        Owner: {owner?.slice(0, 6)}...{owner?.slice(-4)}
      </p>
    </div>
  );
}

// Batch fetch NFT metadata
export async function batchFetchNFTMetadata(
  tokenURIs: string[]
): Promise<NFTMetadata[]> {
  const metadata = await Promise.all(
    tokenURIs.map(async (uri) => {
      try {
        let url = uri;
        if (uri.startsWith('ipfs://')) {
          url = uri.replace('ipfs://', 'https://ipfs.io/ipfs/');
        }

        const response = await fetch(url);
        const data = await response.json();

        if (data.image?.startsWith('ipfs://')) {
          data.image = data.image.replace('ipfs://', 'https://ipfs.io/ipfs/');
        }

        return data;
      } catch (error) {
        console.error('Failed to fetch metadata:', error);
        return null;
      }
    })
  );

  return metadata.filter((m): m is NFTMetadata => m !== null);
}

export default {
  useTokenURI,
  useNFTMetadata,
  useNFTOwner,
  useNFTCollection,
  useNFTBalance,
  NFTCard,
  batchFetchNFTMetadata,
};
