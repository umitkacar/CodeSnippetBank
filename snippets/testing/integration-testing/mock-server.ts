// Mock Server Integration Testing
// Testing with mock HTTP servers

import express, { Express } from 'express';
import { Server } from 'http';

describe('Mock Server Integration', () => {
  let app: Express;
  let server: Server;
  let port: number;

  beforeAll((done) => {
    app = express();
    app.use(express.json());

    app.get('/api/data', (req, res) => {
      res.json({ data: 'test' });
    });

    app.post('/api/data', (req, res) => {
      res.status(201).json(req.body);
    });

    server = app.listen(0, () => {
      port = (server.address() as any).port;
      done();
    });
  });

  afterAll((done) => {
    server.close(done);
  });

  test('fetches data from mock server', async () => {
    const response = await fetch(`http://localhost:${port}/api/data`);
    const data = await response.json();

    expect(data).toEqual({ data: 'test' });
  });

  test('posts data to mock server', async () => {
    const payload = { name: 'test' };
    const response = await fetch(`http://localhost:${port}/api/data`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    expect(data).toEqual(payload);
  });
});
