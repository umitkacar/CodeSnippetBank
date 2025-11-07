/**
 * Next.js Real-time Data patterns
 */
'use client';

// Server-Sent Events (SSE)
import { useEffect, useState } from 'react';

export function useSSE(url: string) {
  const [data, setData] = useState<any[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const eventSource = new EventSource(url);

    eventSource.onopen = () => {
      setIsConnected(true);
    };

    eventSource.onmessage = (event) => {
      const newData = JSON.parse(event.data);
      setData((prev) => [...prev, newData]);
    };

    eventSource.onerror = () => {
      setIsConnected(false);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [url]);

  return { data, isConnected };
}

// Live notifications
export function LiveNotifications() {
  const { data: notifications } = useSSE('/api/notifications/stream');

  return (
    <div>
      {notifications.map((notif, i) => (
        <div key={i}>{notif.message}</div>
      ))}
    </div>
  );
}

// Real-time dashboard
import useSWR from 'swr';

export function RealtimeDashboard() {
  const { data } = useSWR('/api/stats', fetcher, {
    refreshInterval: 5000, // Poll every 5 seconds
  });

  return <div>{JSON.stringify(data)}</div>;
}

const fetcher = (url: string) => fetch(url).then((r) => r.json());

// Optimistic updates
import { useOptimistic } from 'react';

export function OptimisticTodo() {
  const [todos, setTodos] = useState<any[]>([]);
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo: any) => [...state, newTodo]
  );

  const handleAdd = async (todo: any) => {
    addOptimisticTodo(todo);
    await fetch('/api/todos', {
      method: 'POST',
      body: JSON.stringify(todo),
    });
  };

  return (
    <div>
      {optimisticTodos.map((todo) => (
        <div key={todo.id}>{todo.title}</div>
      ))}
    </div>
  );
}
