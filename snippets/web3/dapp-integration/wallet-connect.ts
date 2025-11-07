/**
 * Wallet Connection Hook
 * Connect to various Web3 wallets
 */

import { useConnect, useDisconnect, useAccount } from 'wagmi';
import { useState, useEffect } from 'react';

export function useWalletConnection() {
  const { connect, connectors, isPending, error } = useConnect();
  const { disconnect } = useDisconnect();
  const { address, isConnected, connector } = useAccount();
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');

  useEffect(() => {
    if (isPending) {
      setConnectionStatus('connecting');
    } else if (isConnected) {
      setConnectionStatus('connected');
    } else {
      setConnectionStatus('disconnected');
    }
  }, [isPending, isConnected]);

  const connectWallet = async (connectorId?: string) => {
    const connector = connectorId
      ? connectors.find((c) => c.id === connectorId)
      : connectors[0];

    if (!connector) {
      throw new Error('Connector not found');
    }

    await connect({ connector });
  };

  const disconnectWallet = () => {
    disconnect();
  };

  return {
    address,
    isConnected,
    connector: connector?.name,
    connectors,
    connectionStatus,
    connectWallet,
    disconnectWallet,
    error,
  };
}

// Wallet connection component
export function WalletConnector() {
  const {
    address,
    isConnected,
    connector,
    connectors,
    connectWallet,
    disconnectWallet,
    error,
  } = useWalletConnection();

  if (isConnected) {
    return (
      <div>
        <p>Connected to {connector}</p>
        <p>Address: {address}</p>
        <button onClick={disconnectWallet}>Disconnect</button>
      </div>
    );
  }

  return (
    <div>
      <h3>Connect Wallet</h3>
      {connectors.map((connector) => (
        <button
          key={connector.id}
          onClick={() => connectWallet(connector.id)}
          disabled={!connector.ready}
        >
          Connect with {connector.name}
        </button>
      ))}
      {error && <p>Error: {error.message}</p>}
    </div>
  );
}

export default useWalletConnection;
