// ============================================================================
// Redis Patterns - Caching, Session, Queue, Pub/Sub
// ============================================================================

import { createClient, RedisClientType } from 'redis';

const redis: RedisClientType = createClient({
  url: 'redis://localhost:6379'
});

await redis.connect();

// Snippet 1: Simple string cache
async function cacheUserData(userId: string, userData: any) {
  await redis.set(
    `user:${userId}`,
    JSON.stringify(userData),
    { EX: 3600 } // Expire in 1 hour
  );
}

async function getUserFromCache(userId: string) {
  const cached = await redis.get(`user:${userId}`);
  return cached ? JSON.parse(cached) : null;
}

// Snippet 2: Cache with automatic refresh
async function getCachedOrFetch<T>(
  key: string,
  fetchFn: () => Promise<T>,
  ttl: number = 3600
): Promise<T> {
  const cached = await redis.get(key);

  if (cached) {
    return JSON.parse(cached);
  }

  const data = await fetchFn();
  await redis.set(key, JSON.stringify(data), { EX: ttl });

  return data;
}

// Snippet 3: Session storage
async function createSession(sessionId: string, sessionData: any) {
  await redis.hSet(`session:${sessionId}`, sessionData);
  await redis.expire(`session:${sessionId}`, 86400); // 24 hours
}

async function getSession(sessionId: string) {
  return await redis.hGetAll(`session:${sessionId}`);
}

async function updateSessionField(sessionId: string, field: string, value: string) {
  await redis.hSet(`session:${sessionId}`, field, value);
  await redis.expire(`session:${sessionId}`, 86400);
}

async function destroySession(sessionId: string) {
  await redis.del(`session:${sessionId}`);
}

// Snippet 4: Rate limiting with sliding window
async function checkRateLimit(
  userId: string,
  maxRequests: number = 100,
  windowSeconds: number = 60
): Promise<boolean> {
  const key = `rate_limit:${userId}`;
  const now = Date.now();
  const windowStart = now - (windowSeconds * 1000);

  // Remove old entries
  await redis.zRemRangeByScore(key, 0, windowStart);

  // Count requests in window
  const requestCount = await redis.zCard(key);

  if (requestCount >= maxRequests) {
    return false;
  }

  // Add current request
  await redis.zAdd(key, { score: now, value: `${now}` });
  await redis.expire(key, windowSeconds);

  return true;
}

// Snippet 5: Distributed lock
async function acquireLock(
  lockKey: string,
  lockValue: string,
  ttlSeconds: number = 10
): Promise<boolean> {
  const result = await redis.set(
    `lock:${lockKey}`,
    lockValue,
    { NX: true, EX: ttlSeconds }
  );

  return result === 'OK';
}

async function releaseLock(lockKey: string, lockValue: string): Promise<boolean> {
  const script = `
    if redis.call("get", KEYS[1]) == ARGV[1] then
      return redis.call("del", KEYS[1])
    else
      return 0
    end
  `;

  const result = await redis.eval(script, {
    keys: [`lock:${lockKey}`],
    arguments: [lockValue]
  });

  return result === 1;
}

// Snippet 6: Job queue with Redis List
async function enqueueJob(queueName: string, jobData: any) {
  await redis.lPush(
    `queue:${queueName}`,
    JSON.stringify({ ...jobData, enqueuedAt: Date.now() })
  );
}

async function dequeueJob(queueName: string, timeoutSeconds: number = 0) {
  const result = await redis.brPop(`queue:${queueName}`, timeoutSeconds);
  return result ? JSON.parse(result.element) : null;
}

async function getQueueLength(queueName: string) {
  return await redis.lLen(`queue:${queueName}`);
}

// Snippet 7: Pub/Sub pattern
async function publishMessage(channel: string, message: any) {
  await redis.publish(channel, JSON.stringify(message));
}

async function subscribeToChannel(channel: string, callback: (message: any) => void) {
  const subscriber = redis.duplicate();
  await subscriber.connect();

  await subscriber.subscribe(channel, (message) => {
    callback(JSON.parse(message));
  });

  return subscriber;
}

// Snippet 8: Leaderboard with Sorted Set
async function addToLeaderboard(leaderboardId: string, userId: string, score: number) {
  await redis.zAdd(`leaderboard:${leaderboardId}`, {
    score,
    value: userId
  });
}

async function getLeaderboard(leaderboardId: string, limit: number = 10) {
  return await redis.zRangeWithScores(
    `leaderboard:${leaderboardId}`,
    0,
    limit - 1,
    { REV: true }
  );
}

async function getUserRank(leaderboardId: string, userId: string) {
  const rank = await redis.zRevRank(`leaderboard:${leaderboardId}`, userId);
  return rank !== null ? rank + 1 : null;
}

async function getUserScore(leaderboardId: string, userId: string) {
  return await redis.zScore(`leaderboard:${leaderboardId}`, userId);
}

// Snippet 9: Counting unique visitors with HyperLogLog
async function trackUniqueVisitor(pageId: string, visitorId: string) {
  await redis.pfAdd(`unique_visitors:${pageId}`, visitorId);
}

async function getUniqueVisitorCount(pageId: string) {
  return await redis.pfCount(`unique_visitors:${pageId}`);
}

// Snippet 10: Geospatial index
async function addLocation(
  indexName: string,
  locationId: string,
  longitude: number,
  latitude: number
) {
  await redis.geoAdd(indexName, {
    longitude,
    latitude,
    member: locationId
  });
}

async function findNearbyLocations(
  indexName: string,
  longitude: number,
  latitude: number,
  radiusKm: number,
  limit: number = 10
) {
  return await redis.geoSearch(indexName, {
    longitude,
    latitude
  }, {
    radius: radiusKm,
    unit: 'km'
  }, {
    COUNT: limit,
    WITHDIST: true
  });
}

// Snippet 11: Cache invalidation pattern
async function invalidatePattern(pattern: string) {
  const keys = await redis.keys(pattern);
  if (keys.length > 0) {
    await redis.del(keys);
  }
  return keys.length;
}

// Snippet 12: Multi-get optimization
async function getMultipleUsers(userIds: string[]) {
  const keys = userIds.map(id => `user:${id}`);
  const values = await redis.mGet(keys);

  return values
    .map((val, idx) => ({
      userId: userIds[idx],
      data: val ? JSON.parse(val) : null
    }))
    .filter(item => item.data !== null);
}

// Snippet 13: Atomic counter
async function incrementCounter(counterKey: string, amount: number = 1) {
  return await redis.incrBy(counterKey, amount);
}

async function getAndResetCounter(counterKey: string) {
  const value = await redis.getEx(counterKey, { EX: 0 });
  await redis.del(counterKey);
  return value ? parseInt(value) : 0;
}

// Snippet 14: Bitmap for active users
async function markUserActive(date: string, userId: number) {
  await redis.setBit(`active_users:${date}`, userId, 1);
}

async function isUserActive(date: string, userId: number) {
  return await redis.getBit(`active_users:${date}`, userId);
}

async function countActiveUsers(date: string) {
  return await redis.bitCount(`active_users:${date}`);
}

// Snippet 15: Transaction with MULTI/EXEC
async function transferPoints(fromUser: string, toUser: string, points: number) {
  const multi = redis.multi();

  multi.decrBy(`points:${fromUser}`, points);
  multi.incrBy(`points:${toUser}`, points);
  multi.lPush('transfers', JSON.stringify({
    from: fromUser,
    to: toUser,
    points,
    timestamp: Date.now()
  }));

  return await multi.exec();
}

// Snippet 16: Cache-aside pattern with TTL refresh
async function getWithTTLRefresh<T>(
  key: string,
  fetchFn: () => Promise<T>,
  ttl: number = 3600
): Promise<T> {
  const cached = await redis.get(key);

  if (cached) {
    // Refresh TTL on access
    await redis.expire(key, ttl);
    return JSON.parse(cached);
  }

  const data = await fetchFn();
  await redis.set(key, JSON.stringify(data), { EX: ttl });

  return data;
}

// Snippet 17: Delayed job processing
async function scheduleDelayedJob(jobData: any, delaySeconds: number) {
  const executeAt = Date.now() + (delaySeconds * 1000);
  await redis.zAdd('delayed_jobs', {
    score: executeAt,
    value: JSON.stringify(jobData)
  });
}

async function getReadyJobs() {
  const now = Date.now();
  const jobs = await redis.zRangeByScore('delayed_jobs', 0, now);

  if (jobs.length > 0) {
    await redis.zRemRangeByScore('delayed_jobs', 0, now);
  }

  return jobs.map(job => JSON.parse(job));
}

// Snippet 18: LRU Cache implementation
async function setWithLRU(key: string, value: any, maxSize: number = 1000) {
  const cacheKey = `lru:${key}`;
  const indexKey = 'lru:index';

  // Add to cache
  await redis.set(cacheKey, JSON.stringify(value));

  // Update access time in sorted set
  await redis.zAdd(indexKey, {
    score: Date.now(),
    value: key
  });

  // Evict if over limit
  const size = await redis.zCard(indexKey);
  if (size > maxSize) {
    const toRemove = await redis.zRange(indexKey, 0, size - maxSize - 1);
    await redis.zRem(indexKey, toRemove);
    await redis.del(toRemove.map(k => `lru:${k}`));
  }
}
