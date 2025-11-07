/**
 * Web3 Local Storage Utilities
 * Persist wallet preferences and cache data
 */

import { useState, useEffect } from 'react';

// Storage keys
export const STORAGE_KEYS = {
  LAST_WALLET: 'web3_last_wallet',
  PREFERRED_NETWORK: 'web3_preferred_network',
  SLIPPAGE_TOLERANCE: 'web3_slippage',
  DEADLINE: 'web3_deadline',
  GAS_PRICE: 'web3_gas_price',
  TRANSACTIONS: 'web3_transactions',
  FAVORITES: 'web3_favorites',
};

// Generic storage hook
export function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === 'undefined') {
      return initialValue;
    }

    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return initialValue;
    }
  });

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);

      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.error('Error writing to localStorage:', error);
    }
  };

  const removeValue = () => {
    try {
      setStoredValue(initialValue);
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(key);
      }
    } catch (error) {
      console.error('Error removing from localStorage:', error);
    }
  };

  return [storedValue, setValue, removeValue] as const;
}

// Store last connected wallet
export function useLastConnectedWallet() {
  return useLocalStorage<string | null>(STORAGE_KEYS.LAST_WALLET, null);
}

// Store preferred network
export function usePreferredNetwork() {
  return useLocalStorage<number>(STORAGE_KEYS.PREFERRED_NETWORK, 1); // Default to mainnet
}

// Store transaction history
export interface Transaction {
  hash: string;
  chainId: number;
  timestamp: number;
  description: string;
  status: 'pending' | 'success' | 'failed';
}

export function useTransactionHistory() {
  const [transactions, setTransactions, clearTransactions] = useLocalStorage<
    Transaction[]
  >(STORAGE_KEYS.TRANSACTIONS, []);

  const addTransaction = (tx: Omit<Transaction, 'timestamp'>) => {
    setTransactions((prev) => [
      { ...tx, timestamp: Date.now() },
      ...prev.slice(0, 49), // Keep last 50 transactions
    ]);
  };

  const updateTransaction = (hash: string, updates: Partial<Transaction>) => {
    setTransactions((prev) =>
      prev.map((tx) => (tx.hash === hash ? { ...tx, ...updates } : tx))
    );
  };

  const getRecentTransactions = (count: number = 10) => {
    return transactions.slice(0, count);
  };

  return {
    transactions,
    addTransaction,
    updateTransaction,
    clearTransactions,
    getRecentTransactions,
  };
}

// Store favorite tokens
export interface FavoriteToken {
  address: string;
  symbol: string;
  name: string;
  chainId: number;
}

export function useFavoriteTokens() {
  const [favorites, setFavorites, clearFavorites] = useLocalStorage<
    FavoriteToken[]
  >(STORAGE_KEYS.FAVORITES, []);

  const addFavorite = (token: FavoriteToken) => {
    setFavorites((prev) => {
      const exists = prev.some(
        (t) => t.address === token.address && t.chainId === token.chainId
      );
      if (exists) return prev;
      return [...prev, token];
    });
  };

  const removeFavorite = (address: string, chainId: number) => {
    setFavorites((prev) =>
      prev.filter((t) => !(t.address === address && t.chainId === chainId))
    );
  };

  const isFavorite = (address: string, chainId: number) => {
    return favorites.some(
      (t) => t.address === address && t.chainId === chainId
    );
  };

  return {
    favorites,
    addFavorite,
    removeFavorite,
    isFavorite,
    clearFavorites,
  };
}

// Trading settings
export interface TradingSettings {
  slippageTolerance: number; // in basis points (100 = 1%)
  deadline: number; // in minutes
  expertMode: boolean;
  multihops: boolean;
}

export function useTradingSettings() {
  const [settings, setSettings] = useLocalStorage<TradingSettings>(
    'web3_trading_settings',
    {
      slippageTolerance: 50, // 0.5%
      deadline: 30, // 30 minutes
      expertMode: false,
      multihops: true,
    }
  );

  const updateSettings = (updates: Partial<TradingSettings>) => {
    setSettings((prev) => ({ ...prev, ...updates }));
  };

  return {
    settings,
    updateSettings,
  };
}

// Cache with expiration
export function useCachedData<T>(
  key: string,
  fetchFn: () => Promise<T>,
  ttl: number = 60000 // 1 minute default
) {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      const cached = localStorage.getItem(key);

      if (cached) {
        try {
          const { data: cachedData, timestamp } = JSON.parse(cached);
          if (Date.now() - timestamp < ttl) {
            setData(cachedData);
            return;
          }
        } catch (error) {
          console.error('Error parsing cached data:', error);
        }
      }

      setIsLoading(true);
      try {
        const freshData = await fetchFn();
        setData(freshData);

        localStorage.setItem(
          key,
          JSON.stringify({
            data: freshData,
            timestamp: Date.now(),
          })
        );
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [key, ttl]);

  return { data, isLoading };
}

export default {
  useLocalStorage,
  useLastConnectedWallet,
  usePreferredNetwork,
  useTransactionHistory,
  useFavoriteTokens,
  useTradingSettings,
  useCachedData,
  STORAGE_KEYS,
};
