// REST API Integration Testing
// Comprehensive REST API testing patterns

import request from 'supertest';
import express from 'express';

const createRestApi = () => {
  const app = express();
  app.use(express.json());

  const resources: any[] = [];
  let idCounter = 1;

  // CREATE
  app.post('/api/resources', (req, res) => {
    const resource = { id: idCounter++, ...req.body, createdAt: new Date() };
    resources.push(resource);
    res.status(201).json(resource);
  });

  // READ (all)
  app.get('/api/resources', (req, res) => {
    const { page = 1, limit = 10 } = req.query;
    const startIndex = (Number(page) - 1) * Number(limit);
    const endIndex = startIndex + Number(limit);
    res.json({
      data: resources.slice(startIndex, endIndex),
      total: resources.length,
      page: Number(page),
      limit: Number(limit),
    });
  });

  // READ (one)
  app.get('/api/resources/:id', (req, res) => {
    const resource = resources.find((r) => r.id === Number(req.params.id));
    if (!resource) return res.status(404).json({ error: 'Not found' });
    res.json(resource);
  });

  // UPDATE
  app.put('/api/resources/:id', (req, res) => {
    const index = resources.findIndex((r) => r.id === Number(req.params.id));
    if (index === -1) return res.status(404).json({ error: 'Not found' });
    resources[index] = { ...resources[index], ...req.body, updatedAt: new Date() };
    res.json(resources[index]);
  });

  // PATCH
  app.patch('/api/resources/:id', (req, res) => {
    const index = resources.findIndex((r) => r.id === Number(req.params.id));
    if (index === -1) return res.status(404).json({ error: 'Not found' });
    resources[index] = { ...resources[index], ...req.body };
    res.json(resources[index]);
  });

  // DELETE
  app.delete('/api/resources/:id', (req, res) => {
    const index = resources.findIndex((r) => r.id === Number(req.params.id));
    if (index === -1) return res.status(404).json({ error: 'Not found' });
    resources.splice(index, 1);
    res.status(204).send();
  });

  return app;
};

describe('REST API Integration Tests', () => {
  const app = createRestApi();

  describe('POST /api/resources', () => {
    test('creates new resource', async () => {
      const resource = { name: 'Test Resource', value: 42 };
      const res = await request(app).post('/api/resources').send(resource);

      expect(res.status).toBe(201);
      expect(res.body).toMatchObject(resource);
      expect(res.body).toHaveProperty('id');
      expect(res.body).toHaveProperty('createdAt');
    });
  });

  describe('GET /api/resources', () => {
    test('lists all resources with pagination', async () => {
      const res = await request(app).get('/api/resources').query({ page: 1, limit: 10 });

      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('data');
      expect(res.body).toHaveProperty('total');
      expect(res.body).toHaveProperty('page');
      expect(res.body).toHaveProperty('limit');
    });
  });

  describe('GET /api/resources/:id', () => {
    test('gets single resource', async () => {
      const created = await request(app)
        .post('/api/resources')
        .send({ name: 'Test' });

      const res = await request(app).get(`/api/resources/${created.body.id}`);

      expect(res.status).toBe(200);
      expect(res.body.id).toBe(created.body.id);
    });

    test('returns 404 for non-existent resource', async () => {
      const res = await request(app).get('/api/resources/99999');
      expect(res.status).toBe(404);
    });
  });

  describe('PUT /api/resources/:id', () => {
    test('updates resource', async () => {
      const created = await request(app)
        .post('/api/resources')
        .send({ name: 'Original' });

      const res = await request(app)
        .put(`/api/resources/${created.body.id}`)
        .send({ name: 'Updated' });

      expect(res.status).toBe(200);
      expect(res.body.name).toBe('Updated');
      expect(res.body).toHaveProperty('updatedAt');
    });
  });

  describe('DELETE /api/resources/:id', () => {
    test('deletes resource', async () => {
      const created = await request(app)
        .post('/api/resources')
        .send({ name: 'To Delete' });

      const res = await request(app).delete(`/api/resources/${created.body.id}`);

      expect(res.status).toBe(204);

      const getRes = await request(app).get(`/api/resources/${created.body.id}`);
      expect(getRes.status).toBe(404);
    });
  });
});
