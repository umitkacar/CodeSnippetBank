import { useEffect, useRef, useState } from 'react';

interface WebSocketMessage {
  type: string;
  payload: any;
}

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 1000;
  private messageQueue: string[] = [];
  private listeners: Map<string, Set<(data: any) => void>> = new Map();

  constructor(url: string) {
    this.url = url;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.reconnectAttempts = 0;
          this.flushMessageQueue();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Error parsing message:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('WebSocket closed');
          this.handleReconnect();
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  private handleMessage(message: WebSocketMessage): void {
    const listeners = this.listeners.get(message.type);
    if (listeners) {
      listeners.forEach((callback) => callback(message.payload));
    }
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
      setTimeout(() => {
        this.connect();
      }, this.reconnectInterval * this.reconnectAttempts);
    } else {
      console.error('Max reconnect attempts reached');
    }
  }

  send(type: string, payload: any): void {
    const message = JSON.stringify({ type, payload });

    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(message);
    } else {
      this.messageQueue.push(message);
    }
  }

  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      if (message && this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(message);
      }
    }
  }

  on(type: string, callback: (data: any) => void): () => void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set());
    }
    this.listeners.get(type)!.add(callback);

    // Return unsubscribe function
    return () => {
      this.listeners.get(type)?.delete(callback);
    };
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// React hook for WebSocket
export const useWebSocket = (url: string) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const wsRef = useRef<WebSocketClient | null>(null);

  useEffect(() => {
    wsRef.current = new WebSocketClient(url);

    wsRef.current.connect().then(() => {
      setIsConnected(true);
    });

    return () => {
      wsRef.current?.disconnect();
    };
  }, [url]);

  const sendMessage = (type: string, payload: any) => {
    wsRef.current?.send(type, payload);
  };

  const subscribe = (type: string, callback: (data: any) => void) => {
    return wsRef.current?.on(type, (data) => {
      setLastMessage({ type, data });
      callback(data);
    });
  };

  return { isConnected, sendMessage, subscribe, lastMessage };
};

// Chat WebSocket example
export const useChatWebSocket = (roomId: string) => {
  const [messages, setMessages] = useState<any[]>([]);
  const { isConnected, sendMessage, subscribe } = useWebSocket(
    `wss://api.example.com/chat/${roomId}`
  );

  useEffect(() => {
    const unsubscribe = subscribe?.('message', (message) => {
      setMessages((prev) => [...prev, message]);
    });

    return () => {
      unsubscribe?.();
    };
  }, [subscribe]);

  const sendChatMessage = (text: string) => {
    sendMessage('message', { text, timestamp: Date.now() });
  };

  return { messages, sendChatMessage, isConnected };
};
