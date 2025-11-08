"""
============================================================================
Caching, Partitioning, and Sharding Strategies
============================================================================
"""

import redis
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List
import json
import functools

# ============================================================================
# CACHING STRATEGIES
# ============================================================================

# Snippet 1: Redis cache client setup
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True,
    socket_keepalive=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True,
    max_connections=50
)

# Snippet 2: Cache-aside pattern (lazy loading)
def get_user_with_cache(user_id: int) -> Optional[Dict]:
    """Cache-aside: Check cache first, then database"""
    cache_key = f"user:{user_id}"

    # Try to get from cache
    cached_data = redis_client.get(cache_key)
    if cached_data:
        print(f"Cache HIT for user {user_id}")
        return json.loads(cached_data)

    # Cache miss - get from database
    print(f"Cache MISS for user {user_id}")
    user_data = fetch_user_from_db(user_id)  # Your DB query

    if user_data:
        # Store in cache with TTL
        redis_client.setex(
            cache_key,
            timedelta(hours=1),
            json.dumps(user_data)
        )

    return user_data

# Snippet 3: Write-through cache
def update_user_with_cache(user_id: int, data: Dict) -> bool:
    """Write-through: Update database and cache together"""
    cache_key = f"user:{user_id}"

    # Update database
    success = update_user_in_db(user_id, data)

    if success:
        # Update cache
        redis_client.setex(
            cache_key,
            timedelta(hours=1),
            json.dumps(data)
        )

    return success

# Snippet 4: Write-behind cache (async)
import asyncio
from collections import deque

write_queue = deque()

async def write_behind_cache(user_id: int, data: Dict):
    """Write-behind: Update cache immediately, DB asynchronously"""
    cache_key = f"user:{user_id}"

    # Update cache immediately
    redis_client.setex(
        cache_key,
        timedelta(hours=1),
        json.dumps(data)
    )

    # Queue for async DB write
    write_queue.append((user_id, data))

    # Process queue asynchronously
    if len(write_queue) >= 100:  # Batch write
        await flush_write_queue()

async def flush_write_queue():
    """Batch write queued changes to database"""
    batch = []
    while write_queue and len(batch) < 100:
        batch.append(write_queue.popleft())

    # Bulk update database
    bulk_update_db(batch)

# Snippet 5: Cache invalidation pattern
def invalidate_user_cache(user_id: int):
    """Invalidate cache when data changes"""
    cache_key = f"user:{user_id}"
    redis_client.delete(cache_key)

    # Also invalidate related caches
    redis_client.delete(f"user:{user_id}:orders")
    redis_client.delete(f"user:{user_id}:profile")

# Snippet 6: Multi-level caching
from functools import lru_cache

class MultiLevelCache:
    """In-memory (L1) + Redis (L2) cache"""

    def __init__(self):
        self.l1_cache = {}  # In-memory cache
        self.redis = redis_client

    @lru_cache(maxsize=1000)
    def get(self, key: str) -> Optional[Any]:
        # L1: Check in-memory cache
        if key in self.l1_cache:
            return self.l1_cache[key]

        # L2: Check Redis
        value = self.redis.get(key)
        if value:
            # Promote to L1
            self.l1_cache[key] = json.loads(value)
            return self.l1_cache[key]

        return None

    def set(self, key: str, value: Any, ttl: int = 3600):
        # Set in both levels
        self.l1_cache[key] = value
        self.redis.setex(key, ttl, json.dumps(value))

# Snippet 7: Cache stampede prevention
import time
import threading

class CacheWithLock:
    """Prevent cache stampede with distributed locks"""

    def __init__(self):
        self.redis = redis_client

    def get_or_set(self, key: str, fetch_func, ttl: int = 3600):
        # Try to get from cache
        value = self.redis.get(key)
        if value:
            return json.loads(value)

        # Acquire lock to prevent multiple fetches
        lock_key = f"lock:{key}"
        lock_acquired = self.redis.set(lock_key, "1", nx=True, ex=10)

        if lock_acquired:
            try:
                # Fetch and cache
                value = fetch_func()
                self.redis.setex(key, ttl, json.dumps(value))
                return value
            finally:
                self.redis.delete(lock_key)
        else:
            # Wait for other thread to complete
            time.sleep(0.1)
            return self.get_or_set(key, fetch_func, ttl)

# Snippet 8: Cache warming
def warm_cache():
    """Pre-populate cache with hot data"""
    # Get frequently accessed users
    hot_users = get_top_users_from_db(limit=1000)

    for user in hot_users:
        cache_key = f"user:{user['id']}"
        redis_client.setex(
            cache_key,
            timedelta(hours=2),
            json.dumps(user)
        )

    print(f"Warmed cache with {len(hot_users)} users")

# ============================================================================
# TABLE PARTITIONING (PostgreSQL)
# ============================================================================

# Snippet 9: Range partitioning by date
RANGE_PARTITION_SQL: str = """
-- Create partitioned table
CREATE TABLE orders (
    order_id SERIAL,
    customer_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    total_amount DECIMAL(10, 2),
    status VARCHAR(50)
) PARTITION BY RANGE (order_date);

-- Create partitions for each month
CREATE TABLE orders_2024_01 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE orders_2024_02 PARTITION OF orders
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

CREATE TABLE orders_2024_03 PARTITION OF orders
    FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');

-- Create default partition for future data
CREATE TABLE orders_default PARTITION OF orders DEFAULT;

-- Create indexes on partitions
CREATE INDEX idx_orders_2024_01_customer ON orders_2024_01(customer_id);
CREATE INDEX idx_orders_2024_02_customer ON orders_2024_02(customer_id);
"""

# Snippet 10: List partitioning by region
LIST_PARTITION_SQL: str = """
-- Create partitioned table
CREATE TABLE customers (
    customer_id SERIAL,
    name VARCHAR(255),
    email VARCHAR(255),
    region VARCHAR(50) NOT NULL
) PARTITION BY LIST (region);

-- Create partitions by region
CREATE TABLE customers_us PARTITION OF customers
    FOR VALUES IN ('US', 'USA', 'United States');

CREATE TABLE customers_eu PARTITION OF customers
    FOR VALUES IN ('UK', 'DE', 'FR', 'IT', 'ES');

CREATE TABLE customers_asia PARTITION OF customers
    FOR VALUES IN ('CN', 'JP', 'IN', 'SG');

CREATE TABLE customers_other PARTITION OF customers DEFAULT;
"""

# Snippet 11: Hash partitioning for even distribution
HASH_PARTITION_SQL: str = """
-- Create partitioned table
CREATE TABLE events (
    event_id BIGSERIAL,
    user_id INTEGER NOT NULL,
    event_type VARCHAR(50),
    event_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY HASH (user_id);

-- Create hash partitions (4 partitions)
CREATE TABLE events_p0 PARTITION OF events
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE events_p1 PARTITION OF events
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE events_p2 PARTITION OF events
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE events_p3 PARTITION OF events
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);
"""

# Snippet 12: Automatic partition creation (Python)
def create_monthly_partition(table_name: str, year: int, month: int):
    """Automatically create monthly partitions"""
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    partition_name = f"{table_name}_{year}_{month:02d}"
    start_date = datetime(year, month, 1)
    end_date = start_date + relativedelta(months=1)

    sql = f"""
    CREATE TABLE IF NOT EXISTS {partition_name}
    PARTITION OF {table_name}
    FOR VALUES FROM ('{start_date.date()}') TO ('{end_date.date()}');

    CREATE INDEX IF NOT EXISTS idx_{partition_name}_customer
    ON {partition_name}(customer_id);
    """

    execute_sql(sql)
    print(f"Created partition: {partition_name}")

# Snippet 13: Partition maintenance
def maintain_partitions() -> None:
    """Drop old partitions and create future ones"""
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    # Drop partitions older than 2 years
    cutoff_date = datetime.now() - relativedelta(years=2)
    old_partitions = get_old_partitions('orders', cutoff_date)

    for partition in old_partitions:
        # Archive before dropping
        archive_partition(partition)
        drop_partition(partition)

    # Create partitions for next 3 months
    for i in range(3):
        future_date = datetime.now() + relativedelta(months=i+1)
        create_monthly_partition('orders', future_date.year, future_date.month)

# ============================================================================
# SHARDING STRATEGIES
# ============================================================================

# Snippet 14: Consistent hashing for sharding
class ConsistentHash:
    """Consistent hashing for shard distribution"""

    def __init__(self, nodes: List[str], replicas: int = 150):
        self.replicas = replicas
        self.ring = {}
        self.sorted_keys = []

        for node in nodes:
            self.add_node(node)

    def add_node(self, node: str):
        """Add a node to the hash ring"""
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            self.ring[key] = node
            self.sorted_keys.append(key)

        self.sorted_keys.sort()

    def remove_node(self, node: str):
        """Remove a node from the hash ring"""
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            del self.ring[key]
            self.sorted_keys.remove(key)

    def get_node(self, key: str) -> str:
        """Get the node for a given key"""
        if not self.ring:
            return None

        hash_val = self._hash(key)

        # Find the first node >= hash_val
        for ring_key in self.sorted_keys:
            if ring_key >= hash_val:
                return self.ring[ring_key]

        # Wrap around to first node
        return self.ring[self.sorted_keys[0]]

    def _hash(self, key: str) -> int:
        """Hash function"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

# Snippet 15: Shard-aware database router
class ShardRouter:
    """Route queries to appropriate shards"""

    def __init__(self, shard_configs: Dict[str, str]):
        self.shards = {}
        for shard_name, connection_string in shard_configs.items():
            self.shards[shard_name] = create_connection(connection_string)

        self.hash_ring = ConsistentHash(list(self.shards.keys()))

    def get_shard(self, shard_key: Any) -> Any:
        """Get database connection for shard key"""
        shard_name = self.hash_ring.get_node(str(shard_key))
        return self.shards[shard_name]

    def query(self, shard_key: Any, sql: str, params: tuple = None):
        """Execute query on appropriate shard"""
        shard = self.get_shard(shard_key)
        return execute_query(shard, sql, params)

    def query_all_shards(self, sql: str, params: tuple = None):
        """Execute query on all shards and merge results"""
        results = []
        for shard_name, shard in self.shards.items():
            shard_results = execute_query(shard, sql, params)
            results.extend(shard_results)
        return results

# Snippet 16: Range-based sharding
class RangeShardRouter:
    """Range-based sharding (e.g., by user ID ranges)"""

    def __init__(self):
        self.ranges = [
            (0, 10000000, 'shard1'),
            (10000000, 20000000, 'shard2'),
            (20000000, 30000000, 'shard3'),
            (30000000, float('inf'), 'shard4')
        ]

    def get_shard_name(self, user_id: int) -> str:
        """Determine shard based on user ID range"""
        for start, end, shard_name in self.ranges:
            if start <= user_id < end:
                return shard_name
        return 'shard4'  # Default shard

# Snippet 17: Geographic sharding
class GeoShardRouter:
    """Geographic-based sharding"""

    def __init__(self):
        self.geo_shards = {
            'us': 'shard_us',
            'eu': 'shard_eu',
            'asia': 'shard_asia'
        }

    def get_shard_name(self, country_code: str) -> str:
        """Determine shard based on country"""
        region = self._get_region(country_code)
        return self.geo_shards.get(region, 'shard_us')

    def _get_region(self, country_code: str) -> str:
        """Map country to region"""
        eu_countries = ['UK', 'DE', 'FR', 'IT', 'ES']
        asia_countries = ['CN', 'JP', 'IN', 'SG']

        if country_code in eu_countries:
            return 'eu'
        elif country_code in asia_countries:
            return 'asia'
        return 'us'

# Helper functions (placeholders)
def fetch_user_from_db(user_id: int) -> Dict[str, Any]:
    pass

def update_user_in_db(user_id: int, data: Dict[str, Any]) -> bool:
    pass

def bulk_update_db(batch: List[Any]) -> None:
    pass

def get_top_users_from_db(limit: int) -> List[Dict[str, Any]]:
    pass

def execute_sql(sql: str) -> None:
    pass

def get_old_partitions(table_name: str, cutoff_date: datetime) -> List[str]:
    pass

def archive_partition(partition: str) -> None:
    pass

def drop_partition(partition: str) -> None:
    pass

def create_connection(connection_string: str) -> Any:
    pass

def execute_query(connection: Any, sql: str, params: Optional[tuple] = None) -> Any:
    pass
