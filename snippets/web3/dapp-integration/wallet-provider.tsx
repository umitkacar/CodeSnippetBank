/**
 * Wallet Provider Context
 * Global wallet state management
 */

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useAccount, useDisconnect, useChainId } from 'wagmi';

interface WalletContextType {
  address: string | undefined;
  isConnected: boolean;
  chainId: number;
  disconnect: () => void;
  isLoading: boolean;
}

const WalletContext = createContext<WalletContextType | undefined>(undefined);

export function WalletProvider({ children }: { children: React.ReactNode }) {
  const { address, isConnected, isConnecting } = useAccount();
  const { disconnect } = useDisconnect();
  const chainId = useChainId();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(isConnecting);
  }, [isConnecting]);

  const value = {
    address,
    isConnected,
    chainId,
    disconnect,
    isLoading,
  };

  return (
    <WalletContext.Provider value={value}>{children}</WalletContext.Provider>
  );
}

export function useWallet() {
  const context = useContext(WalletContext);

  if (context === undefined) {
    throw new Error('useWallet must be used within a WalletProvider');
  }

  return context;
}

// Protected route component
export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isConnected, isLoading } = useWallet();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!isConnected) {
    return (
      <div>
        <h2>Connect Your Wallet</h2>
        <p>Please connect your wallet to access this feature</p>
      </div>
    );
  }

  return <>{children}</>;
}

// Network guard component
export function NetworkGuard({
  children,
  requiredChainId,
}: {
  children: React.ReactNode;
  requiredChainId: number;
}) {
  const { chainId } = useWallet();

  if (chainId !== requiredChainId) {
    return (
      <div>
        <h2>Wrong Network</h2>
        <p>Please switch to the correct network</p>
      </div>
    );
  }

  return <>{children}</>;
}

// Wallet button component
export function WalletButton() {
  const { address, isConnected, disconnect } = useWallet();

  if (isConnected && address) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span>
          {address.slice(0, 6)}...{address.slice(-4)}
        </span>
        <button onClick={disconnect}>Disconnect</button>
      </div>
    );
  }

  return <button>Connect Wallet</button>;
}

export default {
  WalletProvider,
  useWallet,
  ProtectedRoute,
  NetworkGuard,
  WalletButton,
};
