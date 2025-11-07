/**
 * Smart Contract Event Listeners
 * Listen to and process contract events
 */

import { useWatchContractEvent } from 'wagmi';
import { Log, BrowserProvider, Contract } from 'ethers';
import { useState, useEffect } from 'react';

// ERC20 Transfer event
const ERC20_ABI = [
  'event Transfer(address indexed from, address indexed to, uint256 value)',
  'event Approval(address indexed owner, address indexed spender, uint256 value)',
];

// Watch contract events with wagmi
export function useWatchTransfers(tokenAddress: string) {
  const [transfers, setTransfers] = useState<any[]>([]);

  useWatchContractEvent({
    address: tokenAddress as `0x${string}`,
    abi: ERC20_ABI,
    eventName: 'Transfer',
    onLogs: (logs) => {
      const newTransfers = logs.map((log) => ({
        from: log.args.from,
        to: log.args.to,
        value: log.args.value,
        blockNumber: log.blockNumber,
        transactionHash: log.transactionHash,
      }));
      setTransfers((prev) => [...prev, ...newTransfers]);
    },
  });

  return transfers;
}

// Watch specific user transfers
export function useWatchUserTransfers(tokenAddress: string, userAddress: string) {
  const [userTransfers, setUserTransfers] = useState<any[]>([]);

  useWatchContractEvent({
    address: tokenAddress as `0x${string}`,
    abi: ERC20_ABI,
    eventName: 'Transfer',
    args: {
      from: userAddress as `0x${string}`,
    },
    onLogs: (logs) => {
      const newTransfers = logs.map((log) => ({
        to: log.args.to,
        value: log.args.value,
        blockNumber: log.blockNumber,
        transactionHash: log.transactionHash,
      }));
      setUserTransfers((prev) => [...prev, ...newTransfers]);
    },
  });

  return userTransfers;
}

// Event listener with ethers.js
export async function listenToEvents(
  provider: BrowserProvider,
  contractAddress: string,
  abi: any[],
  eventName: string,
  callback: (event: any) => void
) {
  const contract = new Contract(contractAddress, abi, provider);

  contract.on(eventName, (...args) => {
    const event = args[args.length - 1];
    callback({
      ...event,
      args: args.slice(0, -1),
    });
  });

  // Return cleanup function
  return () => {
    contract.removeAllListeners(eventName);
  };
}

// Query past events
export async function queryPastEvents(
  provider: BrowserProvider,
  contractAddress: string,
  abi: any[],
  eventName: string,
  fromBlock: number,
  toBlock: number | string = 'latest'
) {
  const contract = new Contract(contractAddress, abi, provider);
  const filter = contract.filters[eventName]();

  const events = await contract.queryFilter(filter, fromBlock, toBlock);

  return events.map((event) => ({
    blockNumber: event.blockNumber,
    transactionHash: event.transactionHash,
    args: event.args,
    data: event.data,
  }));
}

// Real-time event monitor hook
export function useEventMonitor(
  contractAddress: string,
  abi: any[],
  eventName: string
) {
  const [events, setEvents] = useState<any[]>([]);
  const [isListening, setIsListening] = useState(false);

  useWatchContractEvent({
    address: contractAddress as `0x${string}`,
    abi,
    eventName,
    onLogs: (logs) => {
      setEvents((prev) => [...prev, ...logs]);
      setIsListening(true);
    },
  });

  const clearEvents = () => setEvents([]);

  return {
    events,
    isListening,
    clearEvents,
  };
}

// Multi-event listener
export function useMultiEventListener(
  contractAddress: string,
  abi: any[],
  eventNames: string[]
) {
  const [allEvents, setAllEvents] = useState<Record<string, any[]>>({});

  useEffect(() => {
    const initial: Record<string, any[]> = {};
    eventNames.forEach((name) => {
      initial[name] = [];
    });
    setAllEvents(initial);
  }, [eventNames]);

  eventNames.forEach((eventName) => {
    useWatchContractEvent({
      address: contractAddress as `0x${string}`,
      abi,
      eventName,
      onLogs: (logs) => {
        setAllEvents((prev) => ({
          ...prev,
          [eventName]: [...(prev[eventName] || []), ...logs],
        }));
      },
    });
  });

  return allEvents;
}

export default {
  useWatchTransfers,
  useWatchUserTransfers,
  listenToEvents,
  queryPastEvents,
  useEventMonitor,
  useMultiEventListener,
};
