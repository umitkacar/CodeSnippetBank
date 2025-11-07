/**
 * Transaction Status Tracking
 * Monitor and display transaction status
 */

import { useWaitForTransactionReceipt, useTransaction } from 'wagmi';
import { useState, useEffect } from 'react';

export type TransactionStatus =
  | 'idle'
  | 'pending'
  | 'confirming'
  | 'confirmed'
  | 'failed';

// Track transaction status
export function useTransactionStatus(hash?: `0x${string}`) {
  const [status, setStatus] = useState<TransactionStatus>('idle');

  const {
    data: receipt,
    isLoading,
    isSuccess,
    isError,
  } = useWaitForTransactionReceipt({
    hash,
  });

  useEffect(() => {
    if (!hash) {
      setStatus('idle');
    } else if (isLoading) {
      setStatus('confirming');
    } else if (isSuccess) {
      setStatus('confirmed');
    } else if (isError) {
      setStatus('failed');
    }
  }, [hash, isLoading, isSuccess, isError]);

  return {
    status,
    receipt,
    isLoading,
    isSuccess,
    isError,
    confirmations: receipt?.blockNumber ? 1 : 0,
  };
}

// Transaction details hook
export function useTransactionDetails(hash: `0x${string}`) {
  const { data: transaction, isLoading, isError } = useTransaction({
    hash,
  });

  return {
    transaction,
    isLoading,
    isError,
  };
}

// Transaction toast notifications
export function useTransactionToast() {
  const [notifications, setNotifications] = useState<
    Array<{ id: string; status: TransactionStatus; hash: string }>
  >([]);

  const addTransaction = (hash: string) => {
    const id = `tx-${Date.now()}`;
    setNotifications((prev) => [...prev, { id, status: 'pending', hash }]);
    return id;
  };

  const updateTransaction = (id: string, status: TransactionStatus) => {
    setNotifications((prev) =>
      prev.map((notif) => (notif.id === id ? { ...notif, status } : notif))
    );
  };

  const removeTransaction = (id: string) => {
    setNotifications((prev) => prev.filter((notif) => notif.id !== id));
  };

  return {
    notifications,
    addTransaction,
    updateTransaction,
    removeTransaction,
  };
}

// Transaction manager component
export function TransactionManager({ hash }: { hash?: `0x${string}` }) {
  const { status, receipt } = useTransactionStatus(hash);

  const getStatusMessage = () => {
    switch (status) {
      case 'pending':
        return 'Transaction submitted...';
      case 'confirming':
        return 'Waiting for confirmation...';
      case 'confirmed':
        return 'Transaction confirmed!';
      case 'failed':
        return 'Transaction failed';
      default:
        return '';
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'pending':
      case 'confirming':
        return 'yellow';
      case 'confirmed':
        return 'green';
      case 'failed':
        return 'red';
      default:
        return 'gray';
    }
  };

  if (status === 'idle') return null;

  return (
    <div style={{ borderColor: getStatusColor() }}>
      <p>{getStatusMessage()}</p>
      {hash && <p>Hash: {hash.slice(0, 10)}...</p>}
      {receipt && <p>Block: {receipt.blockNumber.toString()}</p>}
    </div>
  );
}

export default {
  useTransactionStatus,
  useTransactionDetails,
  useTransactionToast,
  TransactionManager,
};
