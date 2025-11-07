"""
============================================================================
DynamoDB, Cassandra, and Neo4j Operations
============================================================================
"""

# ============================================================================
# DynamoDB Operations
# ============================================================================

import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Snippet 1: Put item in DynamoDB
def create_user(user_id, user_data):
    table = dynamodb.Table('Users')

    response = table.put_item(
        Item={
            'userId': user_id,
            'email': user_data['email'],
            'name': user_data['name'],
            'createdAt': user_data['createdAt'],
            'metadata': user_data.get('metadata', {})
        }
    )

    return response

# Snippet 2: Get item from DynamoDB
def get_user(user_id):
    table = dynamodb.Table('Users')

    response = table.get_item(
        Key={'userId': user_id}
    )

    return response.get('Item')

# Snippet 3: Query with partition key and sort key
def get_user_orders(user_id, start_date=None):
    table = dynamodb.Table('Orders')

    key_condition = Key('userId').eq(user_id)

    if start_date:
        key_condition &= Key('orderDate').gte(start_date)

    response = table.query(
        KeyConditionExpression=key_condition,
        ScanIndexForward=False,  # Descending order
        Limit=50
    )

    return response['Items']

# Snippet 4: Query with GSI (Global Secondary Index)
def get_orders_by_status(status, limit=100):
    table = dynamodb.Table('Orders')

    response = table.query(
        IndexName='StatusIndex',
        KeyConditionExpression=Key('status').eq(status),
        Limit=limit
    )

    return response['Items']

# Snippet 5: Scan with filter
def scan_high_value_customers(min_lifetime_value):
    table = dynamodb.Table('Users')

    response = table.scan(
        FilterExpression=Attr('lifetimeValue').gte(Decimal(str(min_lifetime_value)))
    )

    return response['Items']

# Snippet 6: Update item
def update_user_email(user_id, new_email):
    table = dynamodb.Table('Users')

    response = table.update_item(
        Key={'userId': user_id},
        UpdateExpression='SET email = :email, updatedAt = :updated',
        ExpressionAttributeValues={
            ':email': new_email,
            ':updated': '2024-01-01T00:00:00Z'
        },
        ReturnValues='ALL_NEW'
    )

    return response['Attributes']

# Snippet 7: Atomic counter
def increment_page_views(page_id):
    table = dynamodb.Table('Pages')

    response = table.update_item(
        Key={'pageId': page_id},
        UpdateExpression='ADD viewCount :inc',
        ExpressionAttributeValues={':inc': 1},
        ReturnValues='UPDATED_NEW'
    )

    return response['Attributes']['viewCount']

# Snippet 8: Conditional update
def update_order_status(order_id, new_status, expected_current_status):
    table = dynamodb.Table('Orders')

    try:
        response = table.update_item(
            Key={'orderId': order_id},
            UpdateExpression='SET #status = :new_status',
            ConditionExpression='#status = :expected_status',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':new_status': new_status,
                ':expected_status': expected_current_status
            },
            ReturnValues='ALL_NEW'
        )
        return response['Attributes']
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return None

# Snippet 9: Batch write
def batch_create_users(users):
    table = dynamodb.Table('Users')

    with table.batch_writer() as batch:
        for user in users:
            batch.put_item(Item=user)

# Snippet 10: Transaction write
def transfer_points(from_user_id, to_user_id, points):
    client = boto3.client('dynamodb')

    response = client.transact_write_items(
        TransactItems=[
            {
                'Update': {
                    'TableName': 'Users',
                    'Key': {'userId': {'S': from_user_id}},
                    'UpdateExpression': 'ADD points :points',
                    'ExpressionAttributeValues': {
                        ':points': {'N': str(-points)}
                    }
                }
            },
            {
                'Update': {
                    'TableName': 'Users',
                    'Key': {'userId': {'S': to_user_id}},
                    'UpdateExpression': 'ADD points :points',
                    'ExpressionAttributeValues': {
                        ':points': {'N': str(points)}
                    }
                }
            }
        ]
    )

    return response


# ============================================================================
# Cassandra Operations
# ============================================================================

from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement, BatchStatement
from datetime import datetime
import uuid

cluster = Cluster(['127.0.0.1'])
session = cluster.connect('myapp')

# Snippet 11: Insert with TTL
def create_session(session_id, user_id, ttl_seconds=3600):
    query = """
        INSERT INTO user_sessions (session_id, user_id, created_at)
        VALUES (?, ?, ?)
        USING TTL ?
    """

    session.execute(query, (session_id, user_id, datetime.now(), ttl_seconds))

# Snippet 12: Query with clustering key
def get_user_events(user_id, start_time=None, end_time=None):
    query = """
        SELECT * FROM user_events
        WHERE user_id = ?
    """
    params = [user_id]

    if start_time and end_time:
        query += " AND event_time >= ? AND event_time <= ?"
        params.extend([start_time, end_time])

    query += " ORDER BY event_time DESC LIMIT 100"

    rows = session.execute(query, params)
    return list(rows)

# Snippet 13: Counter table
def increment_view_count(page_id):
    query = """
        UPDATE page_views
        SET view_count = view_count + 1
        WHERE page_id = ?
    """

    session.execute(query, (page_id,))

# Snippet 14: Batch insert
def batch_insert_events(events):
    batch = BatchStatement()

    query = """
        INSERT INTO user_events (user_id, event_time, event_type, event_data)
        VALUES (?, ?, ?, ?)
    """

    for event in events:
        batch.add(query, (
            event['user_id'],
            event['event_time'],
            event['event_type'],
            event['event_data']
        ))

    session.execute(batch)

# Snippet 15: Time series query with bucketing
def get_metrics_for_day(metric_name, date):
    query = """
        SELECT bucket_time, metric_value
        FROM time_series_metrics
        WHERE metric_name = ? AND date = ?
        ORDER BY bucket_time ASC
    """

    rows = session.execute(query, (metric_name, date))
    return list(rows)

# Snippet 16: Lightweight transaction (Compare-And-Set)
def create_user_if_not_exists(user_id, email, name):
    query = """
        INSERT INTO users (user_id, email, name, created_at)
        VALUES (?, ?, ?, ?)
        IF NOT EXISTS
    """

    result = session.execute(query, (user_id, email, name, datetime.now()))
    return result.was_applied

# Snippet 17: Collection operations
def add_tag_to_product(product_id, tag):
    query = """
        UPDATE products
        SET tags = tags + ?
        WHERE product_id = ?
    """

    session.execute(query, ({tag}, product_id))

def remove_tag_from_product(product_id, tag):
    query = """
        UPDATE products
        SET tags = tags - ?
        WHERE product_id = ?
    """

    session.execute(query, ({tag}, product_id))


# ============================================================================
# Neo4j (Graph Database) Operations
# ============================================================================

from neo4j import GraphDatabase

neo4j_driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "password")
)

# Snippet 18: Create nodes and relationships
def create_user_follows_relationship(follower_id, followee_id):
    with neo4j_driver.session() as session:
        result = session.run("""
            MATCH (follower:User {userId: $follower_id})
            MATCH (followee:User {userId: $followee_id})
            MERGE (follower)-[r:FOLLOWS {createdAt: datetime()}]->(followee)
            RETURN r
        """, follower_id=follower_id, followee_id=followee_id)

        return result.single()

# Snippet 19: Find friends of friends
def get_friends_of_friends(user_id, max_depth=2):
    with neo4j_driver.session() as session:
        result = session.run("""
            MATCH (user:User {userId: $user_id})-[:FOLLOWS*1..2]-(friend)
            WHERE friend.userId <> $user_id
            RETURN DISTINCT friend.userId AS userId, friend.name AS name
            LIMIT 50
        """, user_id=user_id)

        return [dict(record) for record in result]

# Snippet 20: Recommendation based on graph
def get_product_recommendations(user_id, limit=10):
    with neo4j_driver.session() as session:
        result = session.run("""
            MATCH (user:User {userId: $user_id})-[:PURCHASED]->(p:Product)
            MATCH (p)<-[:PURCHASED]-(other:User)-[:PURCHASED]->(rec:Product)
            WHERE NOT (user)-[:PURCHASED]->(rec)
            WITH rec, COUNT(DISTINCT other) AS commonUsers
            RETURN rec.productId AS productId,
                   rec.name AS name,
                   commonUsers
            ORDER BY commonUsers DESC
            LIMIT $limit
        """, user_id=user_id, limit=limit)

        return [dict(record) for record in result]

# Snippet 21: Shortest path between nodes
def find_connection_path(user_id1, user_id2):
    with neo4j_driver.session() as session:
        result = session.run("""
            MATCH path = shortestPath(
                (user1:User {userId: $user_id1})-[:FOLLOWS*]-(user2:User {userId: $user_id2})
            )
            RETURN [node IN nodes(path) | node.name] AS connectionPath,
                   length(path) AS pathLength
        """, user_id1=user_id1, user_id2=user_id2)

        return result.single()

# Snippet 22: Community detection with PageRank
def get_influential_users(limit=20):
    with neo4j_driver.session() as session:
        result = session.run("""
            CALL gds.pageRank.stream('userGraph')
            YIELD nodeId, score
            RETURN gds.util.asNode(nodeId).userId AS userId,
                   gds.util.asNode(nodeId).name AS name,
                   score
            ORDER BY score DESC
            LIMIT $limit
        """, limit=limit)

        return [dict(record) for record in result]

# Snippet 23: Create full-text index and search
def search_users_by_name(search_term):
    with neo4j_driver.session() as session:
        result = session.run("""
            CALL db.index.fulltext.queryNodes('userNameIndex', $search_term)
            YIELD node, score
            RETURN node.userId AS userId,
                   node.name AS name,
                   score
            ORDER BY score DESC
            LIMIT 20
        """, search_term=search_term)

        return [dict(record) for record in result]

# Snippet 24: Aggregate relationship properties
def get_user_interaction_stats(user_id):
    with neo4j_driver.session() as session:
        result = session.run("""
            MATCH (user:User {userId: $user_id})-[r:INTERACTED_WITH]->(other:User)
            RETURN other.userId AS userId,
                   other.name AS name,
                   COUNT(r) AS interactionCount,
                   SUM(r.weight) AS totalWeight
            ORDER BY interactionCount DESC
            LIMIT 10
        """, user_id=user_id)

        return [dict(record) for record in result]
