/**
 * Network Switching
 * Handle multi-chain network switching
 */

import { useSwitchChain, useChainId, useChains } from 'wagmi';
import { mainnet, polygon, arbitrum, optimism, base, sepolia } from 'wagmi/chains';

// Network configurations
export const SUPPORTED_NETWORKS = {
  ethereum: mainnet,
  polygon: polygon,
  arbitrum: arbitrum,
  optimism: optimism,
  base: base,
  sepolia: sepolia,
};

// Switch network hook
export function useNetworkSwitcher() {
  const { switchChain, isPending, error } = useSwitchChain();
  const currentChainId = useChainId();
  const chains = useChains();

  const switchToNetwork = async (chainId: number) => {
    if (currentChainId === chainId) {
      return; // Already on the correct network
    }

    switchChain({ chainId });
  };

  const getCurrentNetwork = () => {
    return chains.find((chain) => chain.id === currentChainId);
  };

  const isCorrectNetwork = (requiredChainId: number) => {
    return currentChainId === requiredChainId;
  };

  return {
    switchToNetwork,
    currentChainId,
    currentNetwork: getCurrentNetwork(),
    isCorrectNetwork,
    supportedChains: chains,
    isPending,
    error,
  };
}

// Network guard hook
export function useNetworkGuard(requiredChainId: number) {
  const { switchToNetwork, currentChainId, isPending } = useNetworkSwitcher();
  const isCorrectNetwork = currentChainId === requiredChainId;

  const ensureCorrectNetwork = async () => {
    if (!isCorrectNetwork) {
      await switchToNetwork(requiredChainId);
    }
  };

  return {
    isCorrectNetwork,
    ensureCorrectNetwork,
    currentChainId,
    requiredChainId,
    isPending,
  };
}

// Network display component
export function NetworkBadge() {
  const { currentNetwork } = useNetworkSwitcher();

  if (!currentNetwork) return null;

  const getNetworkColor = (chainId: number) => {
    switch (chainId) {
      case 1:
        return '#627EEA'; // Ethereum
      case 137:
        return '#8247E5'; // Polygon
      case 42161:
        return '#28A0F0'; // Arbitrum
      case 10:
        return '#FF0420'; // Optimism
      case 8453:
        return '#0052FF'; // Base
      default:
        return '#6B7280';
    }
  };

  return (
    <div
      style={{
        backgroundColor: getNetworkColor(currentNetwork.id),
        padding: '4px 12px',
        borderRadius: '12px',
        color: 'white',
        fontSize: '14px',
      }}
    >
      {currentNetwork.name}
    </div>
  );
}

// Network selector component
export function NetworkSelector() {
  const { switchToNetwork, currentChainId, supportedChains, isPending } =
    useNetworkSwitcher();

  return (
    <div>
      <h3>Select Network</h3>
      {supportedChains.map((chain) => (
        <button
          key={chain.id}
          onClick={() => switchToNetwork(chain.id)}
          disabled={isPending || currentChainId === chain.id}
          style={{
            backgroundColor: currentChainId === chain.id ? '#3b82f6' : '#e5e7eb',
            color: currentChainId === chain.id ? 'white' : 'black',
          }}
        >
          {chain.name}
        </button>
      ))}
    </div>
  );
}

// Get network explorer URL
export function getExplorerUrl(chainId: number, type: 'tx' | 'address' | 'token', value: string): string {
  const explorers: Record<number, string> = {
    1: 'https://etherscan.io',
    137: 'https://polygonscan.com',
    42161: 'https://arbiscan.io',
    10: 'https://optimistic.etherscan.io',
    8453: 'https://basescan.org',
    11155111: 'https://sepolia.etherscan.io',
  };

  const baseUrl = explorers[chainId] || explorers[1];

  switch (type) {
    case 'tx':
      return `${baseUrl}/tx/${value}`;
    case 'address':
      return `${baseUrl}/address/${value}`;
    case 'token':
      return `${baseUrl}/token/${value}`;
    default:
      return baseUrl;
  }
}

// RPC URLs
export const RPC_URLS: Record<number, string> = {
  1: process.env.NEXT_PUBLIC_MAINNET_RPC_URL || 'https://eth.llamarpc.com',
  137: process.env.NEXT_PUBLIC_POLYGON_RPC_URL || 'https://polygon-rpc.com',
  42161: process.env.NEXT_PUBLIC_ARBITRUM_RPC_URL || 'https://arb1.arbitrum.io/rpc',
  10: process.env.NEXT_PUBLIC_OPTIMISM_RPC_URL || 'https://mainnet.optimism.io',
  8453: process.env.NEXT_PUBLIC_BASE_RPC_URL || 'https://mainnet.base.org',
};

export default {
  useNetworkSwitcher,
  useNetworkGuard,
  NetworkBadge,
  NetworkSelector,
  getExplorerUrl,
  SUPPORTED_NETWORKS,
  RPC_URLS,
};
