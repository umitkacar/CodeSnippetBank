/**
 * Ethers.js v6 Setup and Configuration
 * Modern Web3 provider setup with ethers v6
 */

import { ethers, BrowserProvider, JsonRpcProvider, WebSocketProvider } from 'ethers';

// Create provider from browser wallet
export async function createBrowserProvider() {
  if (typeof window.ethereum === 'undefined') {
    throw new Error('MetaMask or Web3 provider not detected');
  }

  const provider = new BrowserProvider(window.ethereum);
  await provider.send('eth_requestAccounts', []);

  return provider;
}

// Create RPC provider
export function createRpcProvider(rpcUrl: string) {
  return new JsonRpcProvider(rpcUrl);
}

// Create WebSocket provider for real-time updates
export function createWebSocketProvider(wsUrl: string) {
  return new WebSocketProvider(wsUrl);
}

// Get signer from provider
export async function getSigner(provider: BrowserProvider) {
  return await provider.getSigner();
}

// Get account address
export async function getAccount(provider: BrowserProvider): Promise<string> {
  const signer = await provider.getSigner();
  return await signer.getAddress();
}

// Get network information
export async function getNetwork(provider: BrowserProvider) {
  const network = await provider.getNetwork();
  return {
    name: network.name,
    chainId: Number(network.chainId),
  };
}

// Get balance
export async function getBalance(
  provider: BrowserProvider,
  address: string
): Promise<string> {
  const balance = await provider.getBalance(address);
  return ethers.formatEther(balance);
}

// Switch network
export async function switchNetwork(chainId: number): Promise<void> {
  if (!window.ethereum) throw new Error('No Web3 provider');

  try {
    await window.ethereum.request({
      method: 'wallet_switchEthereumChain',
      params: [{ chainId: `0x${chainId.toString(16)}` }],
    });
  } catch (error: any) {
    if (error.code === 4902) {
      throw new Error('Network not added to wallet');
    }
    throw error;
  }
}

// Add network to wallet
export async function addNetwork(config: {
  chainId: number;
  chainName: string;
  nativeCurrency: { name: string; symbol: string; decimals: number };
  rpcUrls: string[];
  blockExplorerUrls: string[];
}): Promise<void> {
  if (!window.ethereum) throw new Error('No Web3 provider');

  await window.ethereum.request({
    method: 'wallet_addEthereumChain',
    params: [
      {
        chainId: `0x${config.chainId.toString(16)}`,
        chainName: config.chainName,
        nativeCurrency: config.nativeCurrency,
        rpcUrls: config.rpcUrls,
        blockExplorerUrls: config.blockExplorerUrls,
      },
    ],
  });
}

export default {
  createBrowserProvider,
  createRpcProvider,
  createWebSocketProvider,
  getSigner,
  getAccount,
  getNetwork,
  getBalance,
  switchNetwork,
  addNetwork,
};
