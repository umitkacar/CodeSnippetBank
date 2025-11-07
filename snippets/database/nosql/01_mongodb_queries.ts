// ============================================================================
// MongoDB Queries - Production Ready Examples
// ============================================================================

import { MongoClient, Db, Collection, ObjectId } from 'mongodb';

// Snippet 1: Connection setup
const client = new MongoClient('mongodb://localhost:27017');
const db: Db = client.db('myapp');

// Snippet 2: Find with filters
async function findActiveUsers() {
  const users = await db.collection('users').find({
    status: 'active',
    createdAt: { $gte: new Date('2024-01-01') }
  }).toArray();

  return users;
}

// Snippet 3: Find with projection
async function findUserBasicInfo() {
  const users = await db.collection('users').find(
    { status: 'active' },
    { projection: { name: 1, email: 1, _id: 0 } }
  ).toArray();

  return users;
}

// Snippet 4: Find one with sort
async function findLatestOrder(customerId: string) {
  const order = await db.collection('orders').findOne(
    { customerId: new ObjectId(customerId) },
    { sort: { createdAt: -1 } }
  );

  return order;
}

// Snippet 5: Complex query with $and, $or
async function findPremiumOrders() {
  const orders = await db.collection('orders').find({
    $and: [
      { status: 'completed' },
      {
        $or: [
          { totalAmount: { $gte: 1000 } },
          { isPremiumCustomer: true }
        ]
      }
    ]
  }).toArray();

  return orders;
}

// Snippet 6: Insert documents
async function createUser(userData: any) {
  const result = await db.collection('users').insertOne({
    ...userData,
    createdAt: new Date(),
    updatedAt: new Date()
  });

  return result.insertedId;
}

// Snippet 7: Insert multiple documents
async function createMultipleProducts(products: any[]) {
  const result = await db.collection('products').insertMany(
    products.map(p => ({
      ...p,
      createdAt: new Date(),
      updatedAt: new Date()
    }))
  );

  return result.insertedIds;
}

// Snippet 8: Update one document
async function updateUserEmail(userId: string, newEmail: string) {
  const result = await db.collection('users').updateOne(
    { _id: new ObjectId(userId) },
    {
      $set: { email: newEmail, updatedAt: new Date() }
    }
  );

  return result.modifiedCount;
}

// Snippet 9: Update with $inc operator
async function incrementProductStock(productId: string, quantity: number) {
  const result = await db.collection('products').updateOne(
    { _id: new ObjectId(productId) },
    {
      $inc: { stockQuantity: quantity },
      $set: { updatedAt: new Date() }
    }
  );

  return result.modifiedCount;
}

// Snippet 10: Update with array operators
async function addProductTag(productId: string, tag: string) {
  const result = await db.collection('products').updateOne(
    { _id: new ObjectId(productId) },
    {
      $addToSet: { tags: tag },
      $set: { updatedAt: new Date() }
    }
  );

  return result.modifiedCount;
}

// Snippet 11: Update multiple documents
async function deactivateOldOrders() {
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - 90);

  const result = await db.collection('orders').updateMany(
    {
      status: 'pending',
      createdAt: { $lt: cutoffDate }
    },
    {
      $set: { status: 'cancelled', updatedAt: new Date() }
    }
  );

  return result.modifiedCount;
}

// Snippet 12: Upsert operation
async function upsertUserPreferences(userId: string, preferences: any) {
  const result = await db.collection('userPreferences').updateOne(
    { userId: new ObjectId(userId) },
    {
      $set: {
        ...preferences,
        updatedAt: new Date()
      },
      $setOnInsert: { createdAt: new Date() }
    },
    { upsert: true }
  );

  return result.upsertedId || result.modifiedCount;
}

// Snippet 13: Delete documents
async function deleteUser(userId: string) {
  const result = await db.collection('users').deleteOne({
    _id: new ObjectId(userId)
  });

  return result.deletedCount;
}

// Snippet 14: Delete multiple documents
async function deleteOldLogs() {
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - 30);

  const result = await db.collection('logs').deleteMany({
    createdAt: { $lt: cutoffDate }
  });

  return result.deletedCount;
}

// Snippet 15: Find with regex
async function searchProductsByName(searchTerm: string) {
  const products = await db.collection('products').find({
    name: { $regex: searchTerm, $options: 'i' }
  }).toArray();

  return products;
}

// Snippet 16: Find with array contains
async function findProductsByTag(tag: string) {
  const products = await db.collection('products').find({
    tags: tag
  }).toArray();

  return products;
}

// Snippet 17: Find with nested field query
async function findUsersByCity(city: string) {
  const users = await db.collection('users').find({
    'address.city': city
  }).toArray();

  return users;
}

// Snippet 18: Count documents
async function countActiveUsers() {
  const count = await db.collection('users').countDocuments({
    status: 'active'
  });

  return count;
}

// Snippet 19: Distinct values
async function getDistinctCategories() {
  const categories = await db.collection('products').distinct('category');
  return categories;
}

// Snippet 20: Cursor pagination
async function getPaginatedProducts(page: number = 1, limit: number = 20) {
  const skip = (page - 1) * limit;

  const products = await db.collection('products')
    .find({ isActive: true })
    .sort({ createdAt: -1 })
    .skip(skip)
    .limit(limit)
    .toArray();

  const total = await db.collection('products').countDocuments({ isActive: true });

  return {
    products,
    pagination: {
      page,
      limit,
      total,
      totalPages: Math.ceil(total / limit)
    }
  };
}

// Snippet 21: Bulk write operations
async function bulkUpdateProducts(updates: any[]) {
  const bulkOps = updates.map(update => ({
    updateOne: {
      filter: { _id: new ObjectId(update.id) },
      update: { $set: { ...update.data, updatedAt: new Date() } }
    }
  }));

  const result = await db.collection('products').bulkWrite(bulkOps);
  return result;
}

// Snippet 22: Text search
async function fullTextSearch(searchTerm: string) {
  // Requires text index: db.products.createIndex({ name: "text", description: "text" })
  const products = await db.collection('products').find({
    $text: { $search: searchTerm }
  }, {
    projection: { score: { $meta: 'textScore' } }
  }).sort({ score: { $meta: 'textScore' } }).toArray();

  return products;
}

// Snippet 23: Geospatial query
async function findNearbyStores(longitude: number, latitude: number, maxDistance: number) {
  const stores = await db.collection('stores').find({
    location: {
      $near: {
        $geometry: {
          type: 'Point',
          coordinates: [longitude, latitude]
        },
        $maxDistance: maxDistance
      }
    }
  }).toArray();

  return stores;
}

// Snippet 24: Find with multiple conditions
async function findHighValueOrders() {
  const orders = await db.collection('orders').find({
    $and: [
      { totalAmount: { $gte: 1000 } },
      { status: { $in: ['pending', 'processing'] } },
      { createdAt: { $gte: new Date('2024-01-01') } }
    ]
  }).toArray();

  return orders;
}

// Snippet 25: Replace document
async function replaceProduct(productId: string, newProductData: any) {
  const result = await db.collection('products').replaceOne(
    { _id: new ObjectId(productId) },
    {
      ...newProductData,
      updatedAt: new Date()
    }
  );

  return result.modifiedCount;
}
