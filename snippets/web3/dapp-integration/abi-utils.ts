/**
 * ABI Utilities
 * Parse and work with contract ABIs
 */

import { Interface, Fragment } from 'ethers';

// Parse ABI from JSON
export function parseABI(abiJson: string | any[]): Interface {
  return new Interface(abiJson);
}

// Get function signature
export function getFunctionSignature(abi: any[], functionName: string): string {
  const iface = new Interface(abi);
  const fragment = iface.getFunction(functionName);
  return fragment ? fragment.format('sighash') : '';
}

// Get all function names
export function getFunctionNames(abi: any[]): string[] {
  const iface = new Interface(abi);
  return iface.fragments
    .filter((f) => f.type === 'function')
    .map((f) => f.name);
}

// Get all event names
export function getEventNames(abi: any[]): string[] {
  const iface = new Interface(abi);
  return iface.fragments
    .filter((f) => f.type === 'event')
    .map((f) => f.name);
}

// Get function inputs
export function getFunctionInputs(abi: any[], functionName: string): any[] {
  const iface = new Interface(abi);
  const fragment = iface.getFunction(functionName);
  return fragment ? fragment.inputs : [];
}

// Get function outputs
export function getFunctionOutputs(abi: any[], functionName: string): any[] {
  const iface = new Interface(abi);
  const fragment = iface.getFunction(functionName);
  return fragment ? fragment.outputs : [];
}

// Check if function is view/pure
export function isViewFunction(abi: any[], functionName: string): boolean {
  const iface = new Interface(abi);
  const fragment = iface.getFunction(functionName);
  return fragment ? fragment.stateMutability === 'view' || fragment.stateMutability === 'pure' : false;
}

// Check if function is payable
export function isPayableFunction(abi: any[], functionName: string): boolean {
  const iface = new Interface(abi);
  const fragment = iface.getFunction(functionName);
  return fragment ? fragment.stateMutability === 'payable' : false;
}

// Get event signature
export function getEventSignature(abi: any[], eventName: string): string {
  const iface = new Interface(abi);
  const fragment = iface.getEvent(eventName);
  return fragment ? fragment.format('sighash') : '';
}

// Merge multiple ABIs
export function mergeABIs(...abis: any[][]): any[] {
  const merged: any[] = [];
  const signatures = new Set<string>();

  for (const abi of abis) {
    for (const item of abi) {
      const signature = JSON.stringify(item);
      if (!signatures.has(signature)) {
        signatures.add(signature);
        merged.push(item);
      }
    }
  }

  return merged;
}

// Extract ABI from verified contract (Etherscan)
export async function fetchABIFromEtherscan(
  contractAddress: string,
  apiKey: string,
  chainId: number = 1
): Promise<any[]> {
  const baseUrls: Record<number, string> = {
    1: 'https://api.etherscan.io',
    5: 'https://api-goerli.etherscan.io',
    137: 'https://api.polygonscan.com',
    42161: 'https://api.arbiscan.io',
    10: 'https://api-optimistic.etherscan.io',
  };

  const baseUrl = baseUrls[chainId] || baseUrls[1];

  const response = await fetch(
    `${baseUrl}/api?module=contract&action=getabi&address=${contractAddress}&apikey=${apiKey}`
  );

  const data = await response.json();

  if (data.status !== '1') {
    throw new Error(data.result);
  }

  return JSON.parse(data.result);
}

// Generate human-readable ABI
export function humanReadableABI(abi: any[]): string[] {
  const iface = new Interface(abi);
  return iface.fragments.map((f) => f.format('full'));
}

export default {
  parseABI,
  getFunctionSignature,
  getFunctionNames,
  getEventNames,
  getFunctionInputs,
  getFunctionOutputs,
  isViewFunction,
  isPayableFunction,
  getEventSignature,
  mergeABIs,
  fetchABIFromEtherscan,
  humanReadableABI,
};
