// ============================================================================
// MongoDB Aggregation Pipeline - Advanced Analytics
// ============================================================================

import { MongoClient, Db } from 'mongodb';

const client = new MongoClient('mongodb://localhost:27017');
const db: Db = client.db('myapp');

// Snippet 1: Basic aggregation with $match and $group
async function getSalesByCategory() {
  const result = await db.collection('orders').aggregate([
    { $match: { status: 'completed' } },
    { $unwind: '$items' },
    {
      $group: {
        _id: '$items.category',
        totalSales: { $sum: '$items.amount' },
        orderCount: { $sum: 1 },
        avgOrderValue: { $avg: '$items.amount' }
      }
    },
    { $sort: { totalSales: -1 } }
  ]).toArray();

  return result;
}

// Snippet 2: Aggregation with $lookup (join)
async function getOrdersWithCustomerDetails() {
  const result = await db.collection('orders').aggregate([
    {
      $lookup: {
        from: 'customers',
        localField: 'customerId',
        foreignField: '_id',
        as: 'customer'
      }
    },
    { $unwind: '$customer' },
    {
      $project: {
        orderId: '$_id',
        orderDate: 1,
        totalAmount: 1,
        customerName: '$customer.name',
        customerEmail: '$customer.email'
      }
    }
  ]).toArray();

  return result;
}

// Snippet 3: Multiple $lookup stages
async function getOrdersWithFullDetails() {
  const result = await db.collection('orders').aggregate([
    {
      $lookup: {
        from: 'customers',
        localField: 'customerId',
        foreignField: '_id',
        as: 'customer'
      }
    },
    {
      $lookup: {
        from: 'products',
        localField: 'items.productId',
        foreignField: '_id',
        as: 'productDetails'
      }
    },
    { $unwind: '$customer' },
    {
      $project: {
        orderDate: 1,
        totalAmount: 1,
        customerName: '$customer.name',
        products: '$productDetails.name'
      }
    }
  ]).toArray();

  return result;
}

// Snippet 4: $facet - Multiple aggregations in one query
async function getProductStatistics() {
  const result = await db.collection('products').aggregate([
    {
      $facet: {
        categoryCounts: [
          { $group: { _id: '$category', count: { $sum: 1 } } },
          { $sort: { count: -1 } }
        ],
        priceStats: [
          {
            $group: {
              _id: null,
              avgPrice: { $avg: '$price' },
              minPrice: { $min: '$price' },
              maxPrice: { $max: '$price' }
            }
          }
        ],
        topExpensive: [
          { $sort: { price: -1 } },
          { $limit: 10 },
          { $project: { name: 1, price: 1 } }
        ]
      }
    }
  ]).toArray();

  return result[0];
}

// Snippet 5: Time-based aggregation with $dateTrunc
async function getDailySales() {
  const result = await db.collection('orders').aggregate([
    { $match: { status: 'completed' } },
    {
      $group: {
        _id: {
          $dateTrunc: {
            date: '$orderDate',
            unit: 'day'
          }
        },
        totalSales: { $sum: '$totalAmount' },
        orderCount: { $sum: 1 }
      }
    },
    { $sort: { _id: 1 } }
  ]).toArray();

  return result;
}

// Snippet 6: $bucket - Create ranges
async function groupProductsByPriceRange() {
  const result = await db.collection('products').aggregate([
    {
      $bucket: {
        groupBy: '$price',
        boundaries: [0, 50, 100, 200, 500, 1000],
        default: 'Other',
        output: {
          count: { $sum: 1 },
          products: { $push: '$name' },
          avgPrice: { $avg: '$price' }
        }
      }
    }
  ]).toArray();

  return result;
}

// Snippet 7: $bucketAuto - Automatic bucketing
async function autoBucketProducts() {
  const result = await db.collection('products').aggregate([
    {
      $bucketAuto: {
        groupBy: '$price',
        buckets: 5,
        output: {
          count: { $sum: 1 },
          avgPrice: { $avg: '$price' }
        }
      }
    }
  ]).toArray();

  return result;
}

// Snippet 8: Customer lifetime value calculation
async function calculateCustomerLifetimeValue() {
  const result = await db.collection('orders').aggregate([
    { $match: { status: 'completed' } },
    {
      $group: {
        _id: '$customerId',
        totalOrders: { $sum: 1 },
        lifetimeValue: { $sum: '$totalAmount' },
        avgOrderValue: { $avg: '$totalAmount' },
        firstOrder: { $min: '$orderDate' },
        lastOrder: { $max: '$orderDate' }
      }
    },
    {
      $lookup: {
        from: 'customers',
        localField: '_id',
        foreignField: '_id',
        as: 'customer'
      }
    },
    { $unwind: '$customer' },
    {
      $project: {
        customerName: '$customer.name',
        email: '$customer.email',
        totalOrders: 1,
        lifetimeValue: 1,
        avgOrderValue: 1,
        firstOrder: 1,
        lastOrder: 1,
        daysSinceFirstOrder: {
          $dateDiff: {
            startDate: '$firstOrder',
            endDate: new Date(),
            unit: 'day'
          }
        }
      }
    },
    { $sort: { lifetimeValue: -1 } }
  ]).toArray();

  return result;
}

// Snippet 9: Running totals with $setWindowFields
async function calculateRunningTotals() {
  const result = await db.collection('orders').aggregate([
    { $match: { status: 'completed' } },
    { $sort: { orderDate: 1 } },
    {
      $setWindowFields: {
        sortBy: { orderDate: 1 },
        output: {
          runningTotal: {
            $sum: '$totalAmount',
            window: {
              documents: ['unbounded', 'current']
            }
          },
          movingAverage: {
            $avg: '$totalAmount',
            window: {
              documents: [-6, 0]
            }
          }
        }
      }
    }
  ]).toArray();

  return result;
}

// Snippet 10: Product recommendations based on co-purchases
async function getProductRecommendations(productId: string) {
  const result = await db.collection('orders').aggregate([
    { $match: { 'items.productId': productId } },
    { $unwind: '$items' },
    { $match: { 'items.productId': { $ne: productId } } },
    {
      $group: {
        _id: '$items.productId',
        purchaseCount: { $sum: 1 },
        totalRevenue: { $sum: '$items.amount' }
      }
    },
    {
      $lookup: {
        from: 'products',
        localField: '_id',
        foreignField: '_id',
        as: 'product'
      }
    },
    { $unwind: '$product' },
    {
      $project: {
        productName: '$product.name',
        purchaseCount: 1,
        totalRevenue: 1
      }
    },
    { $sort: { purchaseCount: -1 } },
    { $limit: 10 }
  ]).toArray();

  return result;
}

// Snippet 11: Cohort analysis
async function getCohortAnalysis() {
  const result = await db.collection('orders').aggregate([
    {
      $group: {
        _id: '$customerId',
        firstOrderDate: { $min: '$orderDate' }
      }
    },
    {
      $project: {
        cohort: {
          $dateTrunc: {
            date: '$firstOrderDate',
            unit: 'month'
          }
        }
      }
    },
    {
      $lookup: {
        from: 'orders',
        localField: '_id',
        foreignField: 'customerId',
        as: 'allOrders'
      }
    },
    { $unwind: '$allOrders' },
    {
      $project: {
        cohort: 1,
        orderMonth: {
          $dateTrunc: {
            date: '$allOrders.orderDate',
            unit: 'month'
          }
        },
        orderAmount: '$allOrders.totalAmount'
      }
    },
    {
      $group: {
        _id: {
          cohort: '$cohort',
          orderMonth: '$orderMonth'
        },
        customers: { $addToSet: '$_id' },
        revenue: { $sum: '$orderAmount' }
      }
    },
    {
      $project: {
        cohort: '$_id.cohort',
        orderMonth: '$_id.orderMonth',
        customerCount: { $size: '$customers' },
        revenue: 1
      }
    },
    { $sort: { cohort: 1, orderMonth: 1 } }
  ]).toArray();

  return result;
}

// Snippet 12: Top N per category
async function getTopProductsPerCategory(n: number = 5) {
  const result = await db.collection('orderItems').aggregate([
    {
      $lookup: {
        from: 'products',
        localField: 'productId',
        foreignField: '_id',
        as: 'product'
      }
    },
    { $unwind: '$product' },
    {
      $group: {
        _id: {
          category: '$product.category',
          productId: '$productId'
        },
        productName: { $first: '$product.name' },
        totalSales: { $sum: '$quantity' },
        revenue: { $sum: { $multiply: ['$quantity', '$unitPrice'] } }
      }
    },
    { $sort: { '_id.category': 1, revenue: -1 } },
    {
      $group: {
        _id: '$_id.category',
        products: {
          $push: {
            productId: '$_id.productId',
            productName: '$productName',
            totalSales: '$totalSales',
            revenue: '$revenue'
          }
        }
      }
    },
    {
      $project: {
        category: '$_id',
        topProducts: { $slice: ['$products', n] }
      }
    }
  ]).toArray();

  return result;
}

// Snippet 13: Geographic sales analysis
async function getSalesByRegion() {
  const result = await db.collection('orders').aggregate([
    {
      $lookup: {
        from: 'customers',
        localField: 'customerId',
        foreignField: '_id',
        as: 'customer'
      }
    },
    { $unwind: '$customer' },
    {
      $group: {
        _id: {
          country: '$customer.address.country',
          state: '$customer.address.state'
        },
        totalSales: { $sum: '$totalAmount' },
        orderCount: { $sum: 1 },
        uniqueCustomers: { $addToSet: '$customerId' }
      }
    },
    {
      $project: {
        country: '$_id.country',
        state: '$_id.state',
        totalSales: 1,
        orderCount: 1,
        customerCount: { $size: '$uniqueCustomers' }
      }
    },
    { $sort: { totalSales: -1 } }
  ]).toArray();

  return result;
}

// Snippet 14: RFM (Recency, Frequency, Monetary) Analysis
async function getRFMAnalysis() {
  const result = await db.collection('orders').aggregate([
    { $match: { status: 'completed' } },
    {
      $group: {
        _id: '$customerId',
        lastOrderDate: { $max: '$orderDate' },
        orderCount: { $sum: 1 },
        totalSpent: { $sum: '$totalAmount' }
      }
    },
    {
      $project: {
        recency: {
          $dateDiff: {
            startDate: '$lastOrderDate',
            endDate: new Date(),
            unit: 'day'
          }
        },
        frequency: '$orderCount',
        monetary: '$totalSpent'
      }
    },
    {
      $setWindowFields: {
        sortBy: { recency: 1 },
        output: {
          recencyScore: { $rank: {} }
        }
      }
    },
    {
      $setWindowFields: {
        sortBy: { frequency: -1 },
        output: {
          frequencyScore: { $rank: {} }
        }
      }
    },
    {
      $setWindowFields: {
        sortBy: { monetary: -1 },
        output: {
          monetaryScore: { $rank: {} }
        }
      }
    },
    {
      $lookup: {
        from: 'customers',
        localField: '_id',
        foreignField: '_id',
        as: 'customer'
      }
    },
    { $unwind: '$customer' },
    {
      $project: {
        customerName: '$customer.name',
        email: '$customer.email',
        recency: 1,
        frequency: 1,
        monetary: 1,
        rfmScore: {
          $add: ['$recencyScore', '$frequencyScore', '$monetaryScore']
        }
      }
    },
    { $sort: { rfmScore: 1 } }
  ]).toArray();

  return result;
}
