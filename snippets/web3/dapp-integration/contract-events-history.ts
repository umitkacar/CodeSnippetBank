/**
 * Contract Events History
 * Query and parse historical contract events
 */

import { BrowserProvider, Contract, EventLog } from 'ethers';
import { useState, useEffect } from 'react';

// Query events in range
export async function queryEvents(
  provider: BrowserProvider,
  contractAddress: string,
  abi: any[],
  eventName: string,
  fromBlock: number,
  toBlock: number | string = 'latest',
  filters?: Record<string, any>
): Promise<EventLog[]> {
  const contract = new Contract(contractAddress, abi, provider);
  const filter = filters
    ? contract.filters[eventName](...Object.values(filters))
    : contract.filters[eventName]();

  const events = await contract.queryFilter(filter, fromBlock, toBlock);
  return events as EventLog[];
}

// Get all Transfer events
export async function getTransferHistory(
  provider: BrowserProvider,
  tokenAddress: string,
  userAddress?: string,
  fromBlock: number = 0
): Promise<any[]> {
  const abi = ['event Transfer(address indexed from, address indexed to, uint256 value)'];
  const contract = new Contract(tokenAddress, abi, provider);

  const filter = userAddress
    ? contract.filters.Transfer(userAddress, null)
    : contract.filters.Transfer();

  const events = await contract.queryFilter(filter, fromBlock);

  return events.map((event: any) => ({
    from: event.args.from,
    to: event.args.to,
    value: event.args.value,
    blockNumber: event.blockNumber,
    transactionHash: event.transactionHash,
  }));
}

// Hook for event history
export function useEventHistory(
  contractAddress: string,
  abi: any[],
  eventName: string,
  fromBlock: number = 0
) {
  const [events, setEvents] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchEvents = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const provider = new BrowserProvider((window as any).ethereum);
        const fetchedEvents = await queryEvents(
          provider,
          contractAddress,
          abi,
          eventName,
          fromBlock
        );

        const parsedEvents = fetchedEvents.map((event: any) => ({
          args: event.args,
          blockNumber: event.blockNumber,
          transactionHash: event.transactionHash,
          logIndex: event.logIndex,
        }));

        setEvents(parsedEvents);
      } catch (err) {
        setError(err as Error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchEvents();
  }, [contractAddress, eventName, fromBlock]);

  return { events, isLoading, error };
}

// Paginated event query
export async function queryEventsPaginated(
  provider: BrowserProvider,
  contractAddress: string,
  abi: any[],
  eventName: string,
  startBlock: number,
  endBlock: number,
  pageSize: number = 5000
): Promise<EventLog[]> {
  const contract = new Contract(contractAddress, abi, provider);
  const filter = contract.filters[eventName]();

  const allEvents: EventLog[] = [];
  let currentBlock = startBlock;

  while (currentBlock <= endBlock) {
    const toBlock = Math.min(currentBlock + pageSize - 1, endBlock);
    const events = await contract.queryFilter(filter, currentBlock, toBlock);
    allEvents.push(...(events as EventLog[]));
    currentBlock = toBlock + 1;
  }

  return allEvents;
}

// Event aggregation
export function aggregateEvents<T>(
  events: any[],
  aggregator: (acc: T, event: any) => T,
  initialValue: T
): T {
  return events.reduce(aggregator, initialValue);
}

// Get unique addresses from events
export function getUniqueAddresses(
  events: any[],
  addressField: string = 'from'
): string[] {
  const addresses = events.map((event) => event.args[addressField]);
  return [...new Set(addresses)];
}

export default {
  queryEvents,
  getTransferHistory,
  useEventHistory,
  queryEventsPaginated,
  aggregateEvents,
  getUniqueAddresses,
};
