/**
 * Web3Modal v4 Setup
 * Modern wallet connection modal
 */

import { createWeb3Modal, defaultWagmiConfig } from '@web3modal/wagmi/react';
import { mainnet, polygon, arbitrum, optimism } from 'viem/chains';

// Project configuration
const projectId = process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID!;

const metadata = {
  name: 'My DApp',
  description: 'Web3 Application',
  url: 'https://myapp.com',
  icons: ['https://myapp.com/icon.png'],
};

// Configure chains and transports
const chains = [mainnet, polygon, arbitrum, optimism] as const;

// Create wagmi config
export const wagmiConfig = defaultWagmiConfig({
  chains,
  projectId,
  metadata,
});

// Create Web3Modal
export const web3Modal = createWeb3Modal({
  wagmiConfig,
  projectId,
  chains,
  themeMode: 'dark',
  themeVariables: {
    '--w3m-accent': '#3b82f6',
    '--w3m-border-radius-master': '8px',
  },
  featuredWalletIds: [
    // MetaMask
    'c57ca95b47569778a828d19178114f4db188b89b763c899ba0be274e97267d96',
    // Coinbase Wallet
    'fd20dc426fb37566d803205b19bbc1d4096b248ac04548e3cfb6b3a38bd033aa',
  ],
});

// Hook to use Web3Modal
export function useWeb3Modal() {
  const open = async () => {
    await web3Modal.open();
  };

  const close = () => {
    web3Modal.close();
  };

  return {
    open,
    close,
    modal: web3Modal,
  };
}

// Component wrapper
export function Web3ModalProvider({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}

export default { wagmiConfig, web3Modal, useWeb3Modal };
