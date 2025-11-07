// ============================================================================
// Database Monitoring and Batch Operations
// ============================================================================

import { Pool, PoolClient } from 'pg';
import { performance } from 'perf_hooks';

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'myapp',
  user: 'username',
  password: 'password',
  max: 20
});

// ============================================================================
// PERFORMANCE MONITORING
// ============================================================================

// Snippet 1: Query performance monitoring
class QueryMonitor {
  private metrics: Map<string, {
    count: number;
    totalTime: number;
    avgTime: number;
    maxTime: number;
    minTime: number;
  }> = new Map();

  async monitoredQuery(name: string, query: string, params?: any[]) {
    const start = performance.now();

    try {
      const result = await pool.query(query, params);
      const duration = performance.now() - start;

      this.recordMetric(name, duration);

      if (duration > 1000) {
        console.warn(`Slow query detected: ${name} took ${duration.toFixed(2)}ms`);
      }

      return result.rows;
    } catch (error) {
      const duration = performance.now() - start;
      this.recordMetric(name, duration, true);
      throw error;
    }
  }

  private recordMetric(name: string, duration: number, error: boolean = false) {
    const metric = this.metrics.get(name) || {
      count: 0,
      totalTime: 0,
      avgTime: 0,
      maxTime: 0,
      minTime: Infinity
    };

    metric.count++;
    metric.totalTime += duration;
    metric.avgTime = metric.totalTime / metric.count;
    metric.maxTime = Math.max(metric.maxTime, duration);
    metric.minTime = Math.min(metric.minTime, duration);

    this.metrics.set(name, metric);
  }

  getMetrics() {
    const summary: any = {};
    this.metrics.forEach((metric, name) => {
      summary[name] = {
        ...metric,
        avgTime: metric.avgTime.toFixed(2) + 'ms',
        maxTime: metric.maxTime.toFixed(2) + 'ms',
        minTime: metric.minTime.toFixed(2) + 'ms'
      };
    });
    return summary;
  }

  getSlowestQueries(limit: number = 10) {
    return Array.from(this.metrics.entries())
      .sort((a, b) => b[1].avgTime - a[1].avgTime)
      .slice(0, limit)
      .map(([name, metric]) => ({
        name,
        avgTime: metric.avgTime.toFixed(2) + 'ms',
        count: metric.count
      }));
  }
}

const monitor = new QueryMonitor();

// Snippet 2: Real-time query logging
async function queryWithLogging(sql: string, params?: any[]) {
  const queryId = Math.random().toString(36).substring(7);
  const start = Date.now();

  console.log({
    queryId,
    type: 'query_start',
    sql: sql.substring(0, 100),
    params,
    timestamp: new Date().toISOString()
  });

  try {
    const result = await pool.query(sql, params);
    const duration = Date.now() - start;

    console.log({
      queryId,
      type: 'query_complete',
      duration: `${duration}ms`,
      rowCount: result.rowCount,
      timestamp: new Date().toISOString()
    });

    return result.rows;
  } catch (error) {
    const duration = Date.now() - start;

    console.error({
      queryId,
      type: 'query_error',
      duration: `${duration}ms`,
      error: error.message,
      timestamp: new Date().toISOString()
    });

    throw error;
  }
}

// Snippet 3: Database health check
async function checkDatabaseHealth() {
  const checks = {
    connected: false,
    responseTime: 0,
    activeConnections: 0,
    slowQueries: 0,
    locks: 0,
    timestamp: new Date().toISOString()
  };

  const start = performance.now();

  try {
    // Test basic connectivity
    await pool.query('SELECT 1');
    checks.connected = true;
    checks.responseTime = performance.now() - start;

    // Check active connections
    const connResult = await pool.query(`
      SELECT count(*) as active_connections
      FROM pg_stat_activity
      WHERE state = 'active' AND pid != pg_backend_pid()
    `);
    checks.activeConnections = parseInt(connResult.rows[0].active_connections);

    // Check for slow queries
    const slowResult = await pool.query(`
      SELECT count(*) as slow_queries
      FROM pg_stat_activity
      WHERE state = 'active'
        AND query_start < now() - interval '30 seconds'
        AND pid != pg_backend_pid()
    `);
    checks.slowQueries = parseInt(slowResult.rows[0].slow_queries);

    // Check for locks
    const lockResult = await pool.query(`
      SELECT count(*) as locks
      FROM pg_locks
      WHERE NOT granted
    `);
    checks.locks = parseInt(lockResult.rows[0].locks);

    return checks;
  } catch (error) {
    checks.connected = false;
    return checks;
  }
}

// Snippet 4: Query plan analyzer
async function analyzeQueryPlan(sql: string, params?: any[]) {
  const explainQuery = `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) ${sql}`;

  const result = await pool.query(explainQuery, params);
  const plan = result.rows[0]['QUERY PLAN'][0];

  const analysis = {
    executionTime: plan['Execution Time'],
    planningTime: plan['Planning Time'],
    totalCost: plan.Plan['Total Cost'],
    actualRows: plan.Plan['Actual Rows'],
    nodeType: plan.Plan['Node Type'],
    sharedHitBlocks: plan.Plan['Shared Hit Blocks'],
    sharedReadBlocks: plan.Plan['Shared Read Blocks'],
    recommendations: []
  };

  // Add recommendations based on plan
  if (plan['Execution Time'] > 1000) {
    analysis.recommendations.push('Query execution time exceeds 1 second');
  }

  if (plan.Plan['Node Type'] === 'Seq Scan') {
    analysis.recommendations.push('Sequential scan detected - consider adding index');
  }

  if (plan.Plan['Shared Read Blocks'] > 1000) {
    analysis.recommendations.push('High disk reads - data not cached efficiently');
  }

  return analysis;
}

// ============================================================================
// BATCH OPERATIONS
// ============================================================================

// Snippet 5: Batch insert with COPY
async function batchInsertWithCopy(tableName: string, columns: string[], data: any[][]) {
  const client = await pool.connect();

  try {
    const stream = client.query(
      require('pg-copy-streams').from(
        `COPY ${tableName} (${columns.join(', ')}) FROM STDIN WITH CSV`
      )
    );

    for (const row of data) {
      const csvLine = row.map(val => {
        if (val === null) return '';
        if (typeof val === 'string') return `"${val.replace(/"/g, '""')}"`;
        return val;
      }).join(',');

      stream.write(csvLine + '\n');
    }

    stream.end();

    return new Promise((resolve, reject) => {
      stream.on('finish', resolve);
      stream.on('error', reject);
    });
  } finally {
    client.release();
  }
}

// Snippet 6: Batch insert with multi-value INSERT
async function batchInsert(tableName: string, columns: string[], data: any[][], batchSize: number = 1000) {
  let inserted = 0;

  for (let i = 0; i < data.length; i += batchSize) {
    const batch = data.slice(i, i + batchSize);

    const placeholders = batch.map((_, rowIndex) => {
      const rowPlaceholders = columns.map((_, colIndex) => {
        return `$${rowIndex * columns.length + colIndex + 1}`;
      });
      return `(${rowPlaceholders.join(', ')})`;
    }).join(', ');

    const values = batch.flat();

    const sql = `
      INSERT INTO ${tableName} (${columns.join(', ')})
      VALUES ${placeholders}
    `;

    const result = await pool.query(sql, values);
    inserted += result.rowCount;

    console.log(`Inserted batch ${Math.floor(i / batchSize) + 1}: ${result.rowCount} rows`);
  }

  return inserted;
}

// Snippet 7: Batch update with CASE statement
async function batchUpdate(
  tableName: string,
  updates: Array<{ id: any; updates: Record<string, any> }>
) {
  if (updates.length === 0) return 0;

  const ids = updates.map(u => u.id);
  const updateColumns = Object.keys(updates[0].updates);

  const caseStatements = updateColumns.map(column => {
    const cases = updates.map((update, index) => {
      return `WHEN $${index + 1} THEN $${updates.length + index * updateColumns.length + updateColumns.indexOf(column) + 1}`;
    }).join(' ');

    return `${column} = CASE id ${cases} END`;
  });

  const values = [
    ...ids,
    ...updates.flatMap(u => updateColumns.map(col => u.updates[col]))
  ];

  const sql = `
    UPDATE ${tableName}
    SET ${caseStatements.join(', ')}
    WHERE id = ANY($${values.length + 1})
  `;

  const result = await pool.query(sql, [...values, ids]);
  return result.rowCount;
}

// Snippet 8: Batch delete in chunks
async function batchDelete(
  tableName: string,
  condition: string,
  chunkSize: number = 10000
): Promise<number> {
  let totalDeleted = 0;
  let deleted = 0;

  do {
    const result = await pool.query(`
      DELETE FROM ${tableName}
      WHERE id IN (
        SELECT id FROM ${tableName}
        WHERE ${condition}
        LIMIT $1
      )
    `, [chunkSize]);

    deleted = result.rowCount;
    totalDeleted += deleted;

    console.log(`Deleted ${deleted} rows (total: ${totalDeleted})`);

    // Small delay to avoid overwhelming the database
    await new Promise(resolve => setTimeout(resolve, 100));
  } while (deleted === chunkSize);

  return totalDeleted;
}

// Snippet 9: Parallel batch processing
async function parallelBatchProcess(
  items: any[],
  processor: (item: any) => Promise<void>,
  concurrency: number = 5
) {
  const results = [];
  const queue = [...items];

  async function worker() {
    while (queue.length > 0) {
      const item = queue.shift();
      if (item) {
        try {
          await processor(item);
          results.push({ success: true, item });
        } catch (error) {
          results.push({ success: false, item, error: error.message });
        }
      }
    }
  }

  // Start workers
  const workers = Array(concurrency).fill(null).map(() => worker());
  await Promise.all(workers);

  return results;
}

// Snippet 10: Transaction batch processor
async function transactionBatch(operations: Array<() => Promise<any>>) {
  const client = await pool.connect();

  try {
    await client.query('BEGIN');

    const results = [];
    for (const operation of operations) {
      const result = await operation();
      results.push(result);
    }

    await client.query('COMMIT');
    return results;
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}

// Snippet 11: Upsert batch (INSERT ON CONFLICT)
async function batchUpsert(
  tableName: string,
  columns: string[],
  data: any[][],
  conflictColumns: string[],
  updateColumns: string[]
) {
  const placeholders = data.map((_, rowIndex) => {
    const rowPlaceholders = columns.map((_, colIndex) => {
      return `$${rowIndex * columns.length + colIndex + 1}`;
    });
    return `(${rowPlaceholders.join(', ')})`;
  }).join(', ');

  const updateSet = updateColumns.map(col => `${col} = EXCLUDED.${col}`).join(', ');
  const values = data.flat();

  const sql = `
    INSERT INTO ${tableName} (${columns.join(', ')})
    VALUES ${placeholders}
    ON CONFLICT (${conflictColumns.join(', ')})
    DO UPDATE SET ${updateSet}
  `;

  const result = await pool.query(sql, values);
  return result.rowCount;
}

// Snippet 12: Streaming large result sets
async function* streamLargeResultSet(query: string, params?: any[], chunkSize: number = 1000) {
  const client = await pool.connect();

  try {
    const cursor = client.query(new require('pg-cursor')(query, params));

    while (true) {
      const rows = await new Promise<any[]>((resolve, reject) => {
        cursor.read(chunkSize, (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        });
      });

      if (rows.length === 0) break;

      yield rows;
    }

    cursor.close();
  } finally {
    client.release();
  }
}

// Usage example:
async function processLargeDataset() {
  for await (const chunk of streamLargeResultSet('SELECT * FROM large_table', [], 5000)) {
    console.log(`Processing chunk of ${chunk.length} rows`);
    // Process chunk
  }
}

// Snippet 13: Progress tracking for long operations
async function batchWithProgress(
  items: any[],
  processor: (item: any, index: number) => Promise<void>,
  onProgress?: (current: number, total: number) => void
) {
  const total = items.length;

  for (let i = 0; i < items.length; i++) {
    await processor(items[i], i);

    if (onProgress) {
      onProgress(i + 1, total);
    }

    // Log progress every 10%
    if ((i + 1) % Math.ceil(total / 10) === 0) {
      const percent = ((i + 1) / total * 100).toFixed(1);
      console.log(`Progress: ${percent}% (${i + 1}/${total})`);
    }
  }
}

export {
  monitor,
  queryWithLogging,
  checkDatabaseHealth,
  analyzeQueryPlan,
  batchInsert,
  batchUpdate,
  batchDelete,
  batchUpsert,
  parallelBatchProcess,
  transactionBatch,
  streamLargeResultSet,
  batchWithProgress
};
