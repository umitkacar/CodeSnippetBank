/**
 * Block Explorer Integration
 * Generate explorer links and fetch data
 */

import { useChainId } from 'wagmi';

// Explorer URLs by chain ID
const EXPLORERS: Record<number, { name: string; url: string }> = {
  1: { name: 'Etherscan', url: 'https://etherscan.io' },
  5: { name: 'Goerli Etherscan', url: 'https://goerli.etherscan.io' },
  11155111: { name: 'Sepolia Etherscan', url: 'https://sepolia.etherscan.io' },
  137: { name: 'Polygonscan', url: 'https://polygonscan.com' },
  80001: { name: 'Mumbai Polygonscan', url: 'https://mumbai.polygonscan.com' },
  42161: { name: 'Arbiscan', url: 'https://arbiscan.io' },
  421613: { name: 'Arbitrum Goerli', url: 'https://goerli.arbiscan.io' },
  10: { name: 'Optimism Explorer', url: 'https://optimistic.etherscan.io' },
  420: { name: 'Optimism Goerli', url: 'https://goerli-optimism.etherscan.io' },
  8453: { name: 'Basescan', url: 'https://basescan.org' },
  84531: { name: 'Base Goerli', url: 'https://goerli.basescan.org' },
  56: { name: 'BSCScan', url: 'https://bscscan.com' },
  43114: { name: 'Snowtrace', url: 'https://snowtrace.io' },
  250: { name: 'FTMScan', url: 'https://ftmscan.com' },
};

// Get explorer for current chain
export function useExplorer() {
  const chainId = useChainId();

  const getExplorerUrl = (
    type: 'tx' | 'address' | 'token' | 'block',
    value: string
  ): string => {
    const explorer = EXPLORERS[chainId];
    if (!explorer) return '';

    switch (type) {
      case 'tx':
        return `${explorer.url}/tx/${value}`;
      case 'address':
        return `${explorer.url}/address/${value}`;
      case 'token':
        return `${explorer.url}/token/${value}`;
      case 'block':
        return `${explorer.url}/block/${value}`;
      default:
        return explorer.url;
    }
  };

  const openInExplorer = (
    type: 'tx' | 'address' | 'token' | 'block',
    value: string
  ) => {
    const url = getExplorerUrl(type, value);
    if (url) {
      window.open(url, '_blank');
    }
  };

  return {
    explorerName: EXPLORERS[chainId]?.name || 'Explorer',
    explorerUrl: EXPLORERS[chainId]?.url || '',
    getExplorerUrl,
    openInExplorer,
  };
}

// Transaction link component
export function TransactionLink({
  hash,
  children,
}: {
  hash: string;
  children?: React.ReactNode;
}) {
  const { getExplorerUrl, explorerName } = useExplorer();

  return (
    <a
      href={getExplorerUrl('tx', hash)}
      target="_blank"
      rel="noopener noreferrer"
      style={{ color: '#3b82f6', textDecoration: 'underline' }}
    >
      {children || `${hash.slice(0, 10)}...${hash.slice(-8)}`}
    </a>
  );
}

// Address link component
export function AddressLink({
  address,
  children,
}: {
  address: string;
  children?: React.ReactNode;
}) {
  const { getExplorerUrl } = useExplorer();

  return (
    <a
      href={getExplorerUrl('address', address)}
      target="_blank"
      rel="noopener noreferrer"
      style={{ color: '#3b82f6', textDecoration: 'underline' }}
    >
      {children || `${address.slice(0, 6)}...${address.slice(-4)}`}
    </a>
  );
}

// Token link component
export function TokenLink({
  address,
  symbol,
}: {
  address: string;
  symbol?: string;
}) {
  const { getExplorerUrl } = useExplorer();

  return (
    <a
      href={getExplorerUrl('token', address)}
      target="_blank"
      rel="noopener noreferrer"
      style={{ color: '#3b82f6', textDecoration: 'underline' }}
    >
      {symbol || `${address.slice(0, 6)}...${address.slice(-4)}`}
    </a>
  );
}

// Explorer button component
export function ExplorerButton({
  type,
  value,
  label,
}: {
  type: 'tx' | 'address' | 'token' | 'block';
  value: string;
  label?: string;
}) {
  const { openInExplorer, explorerName } = useExplorer();

  return (
    <button
      onClick={() => openInExplorer(type, value)}
      style={{
        padding: '8px 16px',
        backgroundColor: '#3b82f6',
        color: 'white',
        border: 'none',
        borderRadius: '8px',
        cursor: 'pointer',
      }}
    >
      {label || `View on ${explorerName}`}
    </button>
  );
}

// Shorten address helper
export function shortenAddress(address: string, chars: number = 4): string {
  return `${address.slice(0, chars + 2)}...${address.slice(-chars)}`;
}

// Shorten transaction hash
export function shortenTxHash(hash: string): string {
  return `${hash.slice(0, 10)}...${hash.slice(-8)}`;
}

// Copy to clipboard with toast
export async function copyToClipboard(text: string): Promise<void> {
  try {
    await navigator.clipboard.writeText(text);
    // You can integrate with your toast system here
    console.log('Copied to clipboard');
  } catch (err) {
    console.error('Failed to copy:', err);
  }
}

// Copyable address component
export function CopyableAddress({ address }: { address: string }) {
  const handleCopy = () => {
    copyToClipboard(address);
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <AddressLink address={address} />
      <button
        onClick={handleCopy}
        style={{
          padding: '4px 8px',
          backgroundColor: '#e5e7eb',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
        }}
      >
        Copy
      </button>
    </div>
  );
}

export default {
  useExplorer,
  TransactionLink,
  AddressLink,
  TokenLink,
  ExplorerButton,
  shortenAddress,
  shortenTxHash,
  copyToClipboard,
  CopyableAddress,
  EXPLORERS,
};
