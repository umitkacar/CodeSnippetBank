/**
 * Express CRUD Operations
 */
import express, { Request, Response } from 'express';
import { v4 as uuidv4 } from 'uuid';

const router = express.Router();

interface Item {
  id: string;
  name: string;
  description?: string;
  price: number;
  createdAt: Date;
  updatedAt: Date;
}

// In-memory storage
const items: Map<string, Item> = new Map();

// Create
router.post('/items', (req: Request, res: Response) => {
  const { name, description, price } = req.body;

  if (!name || !price) {
    return res.status(400).json({ error: 'Name and price are required' });
  }

  const item: Item = {
    id: uuidv4(),
    name,
    description,
    price,
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  items.set(item.id, item);
  res.status(201).json(item);
});

// Read all
router.get('/items', (req: Request, res: Response) => {
  const { page = 1, limit = 10 } = req.query;
  const startIndex = (Number(page) - 1) * Number(limit);
  const endIndex = startIndex + Number(limit);

  const allItems = Array.from(items.values());
  const paginatedItems = allItems.slice(startIndex, endIndex);

  res.json({
    items: paginatedItems,
    total: allItems.length,
    page: Number(page),
    totalPages: Math.ceil(allItems.length / Number(limit)),
  });
});

// Read one
router.get('/items/:id', (req: Request, res: Response) => {
  const item = items.get(req.params.id);

  if (!item) {
    return res.status(404).json({ error: 'Item not found' });
  }

  res.json(item);
});

// Update
router.put('/items/:id', (req: Request, res: Response) => {
  const item = items.get(req.params.id);

  if (!item) {
    return res.status(404).json({ error: 'Item not found' });
  }

  const { name, description, price } = req.body;

  const updatedItem: Item = {
    ...item,
    name: name || item.name,
    description: description !== undefined ? description : item.description,
    price: price || item.price,
    updatedAt: new Date(),
  };

  items.set(req.params.id, updatedItem);
  res.json(updatedItem);
});

// Delete
router.delete('/items/:id', (req: Request, res: Response) => {
  if (!items.has(req.params.id)) {
    return res.status(404).json({ error: 'Item not found' });
  }

  items.delete(req.params.id);
  res.status(204).send();
});

export default router;
