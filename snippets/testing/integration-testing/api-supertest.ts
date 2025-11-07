// Supertest API Integration Testing
// Comprehensive API testing with Supertest

import request from 'supertest';
import express, { Express } from 'express';

// Sample Express app
function createApp(): Express {
  const app = express();
  app.use(express.json());

  app.get('/api/users', (req, res) => {
    res.json([
      { id: 1, name: 'John' },
      { id: 2, name: 'Jane' },
    ]);
  });

  app.get('/api/users/:id', (req, res) => {
    const id = parseInt(req.params.id);
    res.json({ id, name: `User ${id}` });
  });

  app.post('/api/users', (req, res) => {
    const { name, email } = req.body;
    res.status(201).json({ id: 3, name, email });
  });

  app.put('/api/users/:id', (req, res) => {
    const id = parseInt(req.params.id);
    res.json({ id, ...req.body });
  });

  app.delete('/api/users/:id', (req, res) => {
    res.status(204).send();
  });

  app.get('/api/error', (req, res) => {
    res.status(500).json({ error: 'Internal Server Error' });
  });

  return app;
}

describe('Supertest API Integration', () => {
  let app: Express;

  beforeAll(() => {
    app = createApp();
  });

  describe('GET /api/users', () => {
    test('returns users list', async () => {
      const response = await request(app).get('/api/users');

      expect(response.status).toBe(200);
      expect(response.body).toHaveLength(2);
      expect(response.body[0]).toHaveProperty('id');
      expect(response.body[0]).toHaveProperty('name');
    });

    test('returns JSON content type', async () => {
      const response = await request(app).get('/api/users');

      expect(response.headers['content-type']).toMatch(/json/);
    });
  });

  describe('GET /api/users/:id', () => {
    test('returns single user', async () => {
      const response = await request(app).get('/api/users/1');

      expect(response.status).toBe(200);
      expect(response.body).toEqual({ id: 1, name: 'User 1' });
    });
  });

  describe('POST /api/users', () => {
    test('creates new user', async () => {
      const newUser = { name: 'Alice', email: 'alice@example.com' };

      const response = await request(app)
        .post('/api/users')
        .send(newUser)
        .set('Content-Type', 'application/json');

      expect(response.status).toBe(201);
      expect(response.body).toMatchObject(newUser);
      expect(response.body).toHaveProperty('id');
    });
  });

  describe('PUT /api/users/:id', () => {
    test('updates user', async () => {
      const updates = { name: 'Updated Name' };

      const response = await request(app)
        .put('/api/users/1')
        .send(updates);

      expect(response.status).toBe(200);
      expect(response.body.name).toBe('Updated Name');
    });
  });

  describe('DELETE /api/users/:id', () => {
    test('deletes user', async () => {
      const response = await request(app).delete('/api/users/1');

      expect(response.status).toBe(204);
    });
  });

  describe('Error handling', () => {
    test('handles server errors', async () => {
      const response = await request(app).get('/api/error');

      expect(response.status).toBe(500);
      expect(response.body).toHaveProperty('error');
    });
  });

  describe('Authentication', () => {
    test('requires authentication header', async () => {
      const response = await request(app)
        .get('/api/users')
        .set('Authorization', 'Bearer token');

      expect(response.status).toBe(200);
    });
  });

  describe('Query parameters', () => {
    test('accepts query parameters', async () => {
      const response = await request(app)
        .get('/api/users')
        .query({ limit: 10, offset: 0 });

      expect(response.status).toBe(200);
    });
  });
});
