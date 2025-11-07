// ============================================================================
// CONNECTION POOLING - Database Connection Management
// ============================================================================

import { Pool, PoolClient, PoolConfig } from 'pg';
import { createPool, Pool as MySQLPool, PoolConnection } from 'mysql2/promise';
import { Sequelize } from 'sequelize';
import { DataSource } from 'typeorm';
import { PrismaClient } from '@prisma/client';

// ============================================================================
// PostgreSQL Connection Pool (pg)
// ============================================================================

// Snippet 1: Basic PostgreSQL connection pool
const pgPoolConfig: PoolConfig = {
  host: 'localhost',
  port: 5432,
  database: 'myapp',
  user: 'username',
  password: 'password',
  max: 20,                    // Maximum pool size
  min: 5,                     // Minimum pool size
  idleTimeoutMillis: 30000,   // Close idle clients after 30s
  connectionTimeoutMillis: 2000,  // Return error if can't connect in 2s
  maxUses: 7500,              // Close connection after 7500 uses
};

const pgPool = new Pool(pgPoolConfig);

// Snippet 2: PostgreSQL pool error handling
pgPool.on('error', (err, client) => {
  console.error('Unexpected error on idle client', err);
  process.exit(-1);
});

pgPool.on('connect', (client) => {
  console.log('New client connected to the pool');
});

pgPool.on('acquire', (client) => {
  console.log('Client acquired from pool');
});

pgPool.on('remove', (client) => {
  console.log('Client removed from pool');
});

// Snippet 3: Execute query with automatic connection management
async function queryWithPool(query: string, params?: any[]) {
  try {
    const result = await pgPool.query(query, params);
    return result.rows;
  } catch (error) {
    console.error('Query error:', error);
    throw error;
  }
}

// Snippet 4: Manual connection checkout and release
async function manualConnectionManagement() {
  const client: PoolClient = await pgPool.connect();

  try {
    await client.query('BEGIN');

    const result1 = await client.query('INSERT INTO users (name) VALUES ($1) RETURNING id', ['John']);
    const userId = result1.rows[0].id;

    await client.query('INSERT INTO profiles (user_id, bio) VALUES ($1, $2)', [userId, 'Developer']);

    await client.query('COMMIT');

    return userId;
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release(); // Always release the client
  }
}

// Snippet 5: PostgreSQL pool monitoring
async function getPoolStats() {
  return {
    totalCount: pgPool.totalCount,      // Total clients in pool
    idleCount: pgPool.idleCount,        // Idle clients
    waitingCount: pgPool.waitingCount,  // Waiting requests
  };
}

// Snippet 6: Graceful pool shutdown
async function shutdownPgPool() {
  await pgPool.end();
  console.log('PostgreSQL pool has ended');
}

// ============================================================================
// MySQL Connection Pool (mysql2)
// ============================================================================

// Snippet 7: MySQL connection pool setup
const mysqlPool: MySQLPool = createPool({
  host: 'localhost',
  port: 3306,
  database: 'myapp',
  user: 'username',
  password: 'password',
  waitForConnections: true,
  connectionLimit: 10,
  maxIdle: 5,
  idleTimeout: 60000,
  queueLimit: 0,
  enableKeepAlive: true,
  keepAliveInitialDelay: 0
});

// Snippet 8: MySQL query execution
async function executeMySQLQuery(sql: string, params?: any[]) {
  try {
    const [rows, fields] = await mysqlPool.execute(sql, params);
    return rows;
  } catch (error) {
    console.error('MySQL query error:', error);
    throw error;
  }
}

// Snippet 9: MySQL transaction with pool
async function mysqlTransaction() {
  const connection: PoolConnection = await mysqlPool.getConnection();

  try {
    await connection.beginTransaction();

    await connection.execute('INSERT INTO users (name) VALUES (?)', ['Jane']);
    await connection.execute('INSERT INTO logs (action) VALUES (?)', ['user_created']);

    await connection.commit();
  } catch (error) {
    await connection.rollback();
    throw error;
  } finally {
    connection.release();
  }
}

// Snippet 10: MySQL pool monitoring
async function getMySQLPoolStats() {
  const pool = mysqlPool.pool;

  return {
    allConnections: pool.allConnections.length,
    freeConnections: pool.freeConnections.length,
    connectionQueue: pool.connectionQueue.length
  };
}

// ============================================================================
// Sequelize Connection Pool
// ============================================================================

// Snippet 11: Sequelize with connection pool
const sequelize = new Sequelize('database', 'username', 'password', {
  host: 'localhost',
  dialect: 'postgres',
  logging: false,
  pool: {
    max: 10,        // Maximum connections
    min: 2,         // Minimum connections
    acquire: 30000, // Maximum time (ms) to get connection
    idle: 10000,    // Maximum idle time before releasing
    evict: 1000,    // Run eviction every 1s
    maxUses: 5000   // Close connection after 5000 queries
  },
  retry: {
    max: 3,         // Maximum retry attempts
    timeout: 3000   // Time between retries
  }
});

// Snippet 12: Sequelize connection test
async function testSequelizeConnection() {
  try {
    await sequelize.authenticate();
    console.log('Sequelize connection established successfully');
  } catch (error) {
    console.error('Unable to connect to database:', error);
  }
}

// Snippet 13: Sequelize graceful shutdown
async function shutdownSequelize() {
  await sequelize.close();
  console.log('Sequelize connections closed');
}

// ============================================================================
// TypeORM Connection Pool
// ============================================================================

// Snippet 14: TypeORM DataSource with pool
const typeormDataSource = new DataSource({
  type: 'postgres',
  host: 'localhost',
  port: 5432,
  username: 'username',
  password: 'password',
  database: 'myapp',
  synchronize: false,
  logging: false,
  entities: [],
  extra: {
    // Connection pool configuration
    max: 20,                    // Maximum pool size
    min: 5,                     // Minimum pool size
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000,
    // Advanced settings
    statement_timeout: 60000,   // Query timeout
    query_timeout: 60000,
    application_name: 'myapp',
  }
});

// Snippet 15: TypeORM initialize and close
async function initializeTypeORM() {
  await typeormDataSource.initialize();
  console.log('TypeORM DataSource initialized');
}

async function shutdownTypeORM() {
  await typeormDataSource.destroy();
  console.log('TypeORM connections closed');
}

// ============================================================================
// Prisma Connection Pool
// ============================================================================

// Snippet 16: Prisma Client with connection pool
const prisma = new PrismaClient({
  datasources: {
    db: {
      url: 'postgresql://username:password@localhost:5432/myapp?connection_limit=10&pool_timeout=20'
    }
  },
  log: [
    { level: 'query', emit: 'event' },
    { level: 'error', emit: 'stdout' },
  ]
});

// Snippet 17: Prisma connection pool monitoring
prisma.$on('query', (e) => {
  console.log('Query: ' + e.query);
  console.log('Duration: ' + e.duration + 'ms');
});

// Snippet 18: Prisma graceful shutdown
async function shutdownPrisma() {
  await prisma.$disconnect();
  console.log('Prisma disconnected');
}

// ============================================================================
// Advanced Connection Pool Patterns
// ============================================================================

// Snippet 19: Dynamic pool sizing based on load
class AdaptivePool {
  private pool: Pool;
  private metrics = {
    activeConnections: 0,
    queuedRequests: 0,
    avgResponseTime: 0
  };

  constructor(config: PoolConfig) {
    this.pool = new Pool(config);
    this.monitorAndAdjust();
  }

  private monitorAndAdjust() {
    setInterval(() => {
      const stats = {
        total: this.pool.totalCount,
        idle: this.pool.idleCount,
        waiting: this.pool.waitingCount
      };

      // If queue is building up and we have capacity, increase pool
      if (stats.waiting > 5 && stats.total < 50) {
        console.log('Increasing pool size due to high demand');
        // Dynamically adjust pool (implementation depends on driver)
      }

      // If mostly idle, consider reducing pool size
      if (stats.idle > stats.total * 0.8 && stats.total > 10) {
        console.log('High idle connection ratio');
      }
    }, 10000);
  }

  async query(sql: string, params?: any[]) {
    const start = Date.now();
    try {
      const result = await this.pool.query(sql, params);
      const duration = Date.now() - start;

      // Update metrics
      this.updateMetrics(duration);

      return result.rows;
    } catch (error) {
      throw error;
    }
  }

  private updateMetrics(duration: number) {
    this.metrics.avgResponseTime =
      (this.metrics.avgResponseTime * 0.9) + (duration * 0.1);
  }

  getMetrics() {
    return { ...this.metrics };
  }
}

// Snippet 20: Health check for connection pool
async function checkPoolHealth(pool: Pool) {
  try {
    const client = await pool.connect();
    const result = await client.query('SELECT 1');
    client.release();

    const stats = {
      healthy: true,
      totalConnections: pool.totalCount,
      idleConnections: pool.idleCount,
      waitingRequests: pool.waitingCount,
      timestamp: new Date()
    };

    return stats;
  } catch (error) {
    return {
      healthy: false,
      error: error.message,
      timestamp: new Date()
    };
  }
}

// Snippet 21: Connection pool with retry logic
async function queryWithRetry(
  pool: Pool,
  query: string,
  params?: any[],
  maxRetries: number = 3
) {
  let lastError;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await pool.query(query, params);
    } catch (error) {
      lastError = error;
      console.error(`Query attempt ${attempt} failed:`, error.message);

      if (attempt < maxRetries) {
        // Exponential backoff
        await new Promise(resolve =>
          setTimeout(resolve, Math.pow(2, attempt) * 1000)
        );
      }
    }
  }

  throw lastError;
}

// Snippet 22: Cleanup on application shutdown
process.on('SIGINT', async () => {
  console.log('Gracefully shutting down...');

  await Promise.all([
    pgPool.end(),
    mysqlPool.end(),
    sequelize.close(),
    typeormDataSource.destroy(),
    prisma.$disconnect()
  ]);

  console.log('All database connections closed');
  process.exit(0);
});

export {
  pgPool,
  mysqlPool,
  sequelize,
  typeormDataSource,
  prisma,
  queryWithPool,
  executeMySQLQuery,
  checkPoolHealth,
  queryWithRetry
};
