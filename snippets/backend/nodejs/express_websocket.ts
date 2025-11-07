/**
 * Express WebSocket Integration
 */
import express from 'express';
import { WebSocket, WebSocketServer } from 'ws';
import { createServer } from 'http';

const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server });

interface Client {
  id: string;
  ws: WebSocket;
  room?: string;
}

const clients = new Map<string, Client>();

// WebSocket connection handler
wss.on('connection', (ws: WebSocket, req) => {
  const clientId = Math.random().toString(36).substring(7);

  const client: Client = {
    id: clientId,
    ws,
  };

  clients.set(clientId, client);

  console.log(`Client ${clientId} connected`);

  // Send welcome message
  ws.send(JSON.stringify({
    type: 'connection',
    message: 'Connected to WebSocket server',
    clientId,
  }));

  // Handle messages
  ws.on('message', (data: Buffer) => {
    try {
      const message = JSON.parse(data.toString());

      switch (message.type) {
        case 'join':
          client.room = message.room;
          broadcast(message.room, {
            type: 'user_joined',
            clientId,
            room: message.room,
          }, clientId);
          break;

        case 'message':
          if (client.room) {
            broadcast(client.room, {
              type: 'message',
              clientId,
              content: message.content,
              timestamp: new Date().toISOString(),
            }, clientId);
          }
          break;

        case 'private':
          sendToClient(message.targetId, {
            type: 'private_message',
            from: clientId,
            content: message.content,
          });
          break;

        default:
          ws.send(JSON.stringify({ error: 'Unknown message type' }));
      }
    } catch (error) {
      ws.send(JSON.stringify({ error: 'Invalid message format' }));
    }
  });

  // Handle disconnect
  ws.on('close', () => {
    if (client.room) {
      broadcast(client.room, {
        type: 'user_left',
        clientId,
      }, clientId);
    }
    clients.delete(clientId);
    console.log(`Client ${clientId} disconnected`);
  });

  // Handle errors
  ws.on('error', (error) => {
    console.error(`WebSocket error for client ${clientId}:`, error);
  });
});

// Broadcast to room
function broadcast(room: string, message: any, excludeId?: string) {
  const data = JSON.stringify(message);

  clients.forEach((client) => {
    if (client.room === room && client.id !== excludeId && client.ws.readyState === WebSocket.OPEN) {
      client.ws.send(data);
    }
  });
}

// Send to specific client
function sendToClient(clientId: string, message: any) {
  const client = clients.get(clientId);

  if (client && client.ws.readyState === WebSocket.OPEN) {
    client.ws.send(JSON.stringify(message));
  }
}

// REST API endpoints
app.get('/ws/clients', (req, res) => {
  const clientList = Array.from(clients.values()).map(client => ({
    id: client.id,
    room: client.room,
  }));

  res.json({ clients: clientList, count: clientList.length });
});

app.get('/ws/rooms', (req, res) => {
  const rooms = new Map<string, number>();

  clients.forEach(client => {
    if (client.room) {
      rooms.set(client.room, (rooms.get(client.room) || 0) + 1);
    }
  });

  res.json({ rooms: Array.from(rooms.entries()).map(([name, count]) => ({ name, count })) });
});

const PORT = process.env.PORT || 3000;

server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

export { app, server, wss };
