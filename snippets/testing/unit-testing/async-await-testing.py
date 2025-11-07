"""
Async/Await Testing in Python
Comprehensive async testing patterns with pytest-asyncio
"""

import pytest
import asyncio
from typing import List, Dict, Any
from datetime import datetime


# Async functions to test
async def fetch_data(delay: float = 0.1) -> Dict[str, Any]:
    """Simulate async data fetching"""
    await asyncio.sleep(delay)
    return {"data": "test", "timestamp": datetime.now().isoformat()}


async def process_items(items: List[int]) -> List[int]:
    """Process items asynchronously"""
    await asyncio.sleep(0.1)
    return [item * 2 for item in items]


async def failing_operation() -> None:
    """Async operation that fails"""
    await asyncio.sleep(0.1)
    raise ValueError("Operation failed")


class AsyncDataService:
    """Async service class for testing"""

    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user by ID"""
        await asyncio.sleep(0.1)
        return {"id": user_id, "name": f"User {user_id}"}

    async def get_users(self, user_ids: List[int]) -> List[Dict[str, Any]]:
        """Get multiple users"""
        tasks = [self.get_user(uid) for uid in user_ids]
        return await asyncio.gather(*tasks)

    async def create_user(self, name: str, email: str) -> Dict[str, Any]:
        """Create new user"""
        await asyncio.sleep(0.1)
        return {"id": 1, "name": name, "email": email}

    async def update_user(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user"""
        await asyncio.sleep(0.1)
        return {"id": user_id, **data}

    async def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        await asyncio.sleep(0.1)
        return True


# Basic async tests
@pytest.mark.asyncio
async def test_fetch_data():
    """Test async data fetching"""
    result = await fetch_data()
    assert "data" in result
    assert result["data"] == "test"
    assert "timestamp" in result


@pytest.mark.asyncio
async def test_process_items():
    """Test async item processing"""
    items = [1, 2, 3, 4, 5]
    result = await process_items(items)
    assert result == [2, 4, 6, 8, 10]


@pytest.mark.asyncio
async def test_failing_operation():
    """Test async operation that fails"""
    with pytest.raises(ValueError, match="Operation failed"):
        await failing_operation()


# Testing async class methods
@pytest.fixture
async def async_service():
    """Fixture providing async service"""
    return AsyncDataService()


@pytest.mark.asyncio
async def test_get_user(async_service):
    """Test getting single user"""
    user = await async_service.get_user(1)
    assert user["id"] == 1
    assert user["name"] == "User 1"


@pytest.mark.asyncio
async def test_get_multiple_users(async_service):
    """Test getting multiple users"""
    users = await async_service.get_users([1, 2, 3])
    assert len(users) == 3
    assert users[0]["id"] == 1
    assert users[1]["id"] == 2
    assert users[2]["id"] == 3


@pytest.mark.asyncio
async def test_create_user(async_service):
    """Test user creation"""
    user = await async_service.create_user("John Doe", "john@example.com")
    assert user["name"] == "John Doe"
    assert user["email"] == "john@example.com"


@pytest.mark.asyncio
async def test_update_user(async_service):
    """Test user update"""
    updated = await async_service.update_user(1, {"name": "Updated Name"})
    assert updated["id"] == 1
    assert updated["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_delete_user(async_service):
    """Test user deletion"""
    result = await async_service.delete_user(1)
    assert result is True


# Concurrent async tests
@pytest.mark.asyncio
async def test_concurrent_operations(async_service):
    """Test concurrent async operations"""
    # Run multiple operations concurrently
    results = await asyncio.gather(
        async_service.get_user(1),
        async_service.get_user(2),
        async_service.get_user(3),
    )

    assert len(results) == 3
    assert all("id" in user for user in results)


@pytest.mark.asyncio
async def test_parallel_processing():
    """Test parallel async processing"""
    async def process_batch(batch: List[int]) -> List[int]:
        await asyncio.sleep(0.1)
        return [x * 2 for x in batch]

    batches = [[1, 2], [3, 4], [5, 6]]
    results = await asyncio.gather(*[process_batch(batch) for batch in batches])

    assert results == [[2, 4], [6, 8], [10, 12]]


# Async context managers
class AsyncResource:
    """Async resource with context manager"""

    def __init__(self):
        self.connected = False

    async def __aenter__(self):
        await asyncio.sleep(0.05)
        self.connected = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await asyncio.sleep(0.05)
        self.connected = False

    async def fetch(self) -> str:
        if not self.connected:
            raise RuntimeError("Not connected")
        await asyncio.sleep(0.05)
        return "data"


@pytest.mark.asyncio
async def test_async_context_manager():
    """Test async context manager"""
    async with AsyncResource() as resource:
        assert resource.connected is True
        data = await resource.fetch()
        assert data == "data"

    assert resource.connected is False


# Async generators
async def async_generator(n: int):
    """Async generator for testing"""
    for i in range(n):
        await asyncio.sleep(0.05)
        yield i


@pytest.mark.asyncio
async def test_async_generator():
    """Test async generator"""
    results = []
    async for value in async_generator(5):
        results.append(value)

    assert results == [0, 1, 2, 3, 4]


# Timeout testing
@pytest.mark.asyncio
async def test_with_timeout():
    """Test async operation with timeout"""
    async def slow_operation():
        await asyncio.sleep(2)
        return "done"

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_operation(), timeout=0.5)


@pytest.mark.asyncio
async def test_successful_within_timeout():
    """Test operation completes within timeout"""
    async def fast_operation():
        await asyncio.sleep(0.1)
        return "done"

    result = await asyncio.wait_for(fast_operation(), timeout=1.0)
    assert result == "done"


# Error handling in concurrent operations
@pytest.mark.asyncio
async def test_concurrent_with_errors():
    """Test handling errors in concurrent operations"""
    async def may_fail(value: int) -> int:
        await asyncio.sleep(0.05)
        if value < 0:
            raise ValueError("Negative value")
        return value * 2

    with pytest.raises(ValueError):
        await asyncio.gather(
            may_fail(1),
            may_fail(-1),  # This will fail
            may_fail(3),
        )


@pytest.mark.asyncio
async def test_concurrent_with_return_exceptions():
    """Test concurrent operations returning exceptions"""
    async def may_fail(value: int) -> int:
        await asyncio.sleep(0.05)
        if value < 0:
            raise ValueError("Negative value")
        return value * 2

    results = await asyncio.gather(
        may_fail(1),
        may_fail(-1),
        may_fail(3),
        return_exceptions=True,
    )

    assert results[0] == 2
    assert isinstance(results[1], ValueError)
    assert results[2] == 6


# Async fixtures with cleanup
@pytest.fixture
async def async_database():
    """Async fixture with setup and teardown"""
    # Setup
    db = {"connected": True, "data": {}}
    await asyncio.sleep(0.05)

    yield db

    # Teardown
    await asyncio.sleep(0.05)
    db["connected"] = False


@pytest.mark.asyncio
async def test_with_async_fixture(async_database):
    """Test using async fixture"""
    assert async_database["connected"] is True
    async_database["data"]["test"] = "value"
    assert async_database["data"]["test"] == "value"


# Async mocking
@pytest.mark.asyncio
async def test_async_mock():
    """Test with async mock"""
    from unittest.mock import AsyncMock

    mock_service = AsyncMock()
    mock_service.get_data.return_value = {"result": "mocked"}

    result = await mock_service.get_data()
    assert result == {"result": "mocked"}
    mock_service.get_data.assert_called_once()


@pytest.mark.asyncio
async def test_async_mock_side_effect():
    """Test async mock with side effect"""
    from unittest.mock import AsyncMock

    mock_service = AsyncMock()
    mock_service.get_data.side_effect = [
        {"result": "first"},
        {"result": "second"},
    ]

    first = await mock_service.get_data()
    second = await mock_service.get_data()

    assert first == {"result": "first"}
    assert second == {"result": "second"}


# Parameterized async tests
@pytest.mark.asyncio
@pytest.mark.parametrize("delay,expected", [
    (0.05, True),
    (0.1, True),
    (0.15, True),
])
async def test_parametrized_async(delay, expected):
    """Test parameterized async function"""
    async def delayed_check(delay: float) -> bool:
        await asyncio.sleep(delay)
        return True

    result = await delayed_check(delay)
    assert result == expected


# Event loop testing
@pytest.mark.asyncio
async def test_event_loop_operations():
    """Test event loop operations"""
    loop = asyncio.get_event_loop()

    async def task1():
        await asyncio.sleep(0.1)
        return "task1"

    async def task2():
        await asyncio.sleep(0.1)
        return "task2"

    # Create tasks
    t1 = loop.create_task(task1())
    t2 = loop.create_task(task2())

    # Wait for tasks
    results = await asyncio.gather(t1, t2)

    assert results == ["task1", "task2"]
