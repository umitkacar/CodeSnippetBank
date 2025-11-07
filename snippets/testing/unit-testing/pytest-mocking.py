"""
Pytest Mocking with pytest-mock
Comprehensive mocking examples using pytest-mock and unittest.mock
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call, PropertyMock
from typing import Dict, List


# Class to test
class UserService:
    """User service for testing"""

    def __init__(self, db_client):
        self.db_client = db_client

    def get_user(self, user_id: int) -> Dict:
        return self.db_client.fetch_one("users", user_id)

    def get_all_users(self) -> List[Dict]:
        return self.db_client.fetch_all("users")

    def create_user(self, user_data: Dict) -> Dict:
        return self.db_client.insert("users", user_data)

    def delete_user(self, user_id: int) -> bool:
        return self.db_client.delete("users", user_id)


# Basic mocking with pytest-mock
def test_mock_function(mocker):
    """Test with mocked function"""
    mock_func = mocker.Mock(return_value=42)
    result = mock_func(1, 2, 3)

    assert result == 42
    mock_func.assert_called_once_with(1, 2, 3)


def test_mock_method(mocker):
    """Test with mocked method"""
    mock_db = mocker.Mock()
    mock_db.fetch_one.return_value = {"id": 1, "name": "John"}

    service = UserService(mock_db)
    user = service.get_user(1)

    assert user["name"] == "John"
    mock_db.fetch_one.assert_called_once_with("users", 1)


# Mock return values
def test_mock_return_values(mocker):
    """Test mock with different return values"""
    mock_func = mocker.Mock()
    mock_func.return_value = "default"

    assert mock_func() == "default"
    assert mock_func() == "default"


def test_mock_side_effect(mocker):
    """Test mock with side effect"""
    mock_func = mocker.Mock(side_effect=[1, 2, 3])

    assert mock_func() == 1
    assert mock_func() == 2
    assert mock_func() == 3


def test_mock_exception(mocker):
    """Test mock raising exception"""
    mock_func = mocker.Mock(side_effect=ValueError("Invalid input"))

    with pytest.raises(ValueError, match="Invalid input"):
        mock_func()


# Patching with pytest-mock
def test_patch_function(mocker):
    """Test patching a function"""
    mocker.patch('os.path.exists', return_value=True)
    import os
    assert os.path.exists('/fake/path') is True


def test_patch_method(mocker):
    """Test patching a method"""
    mock_db = mocker.Mock()
    mock_db.fetch_all.return_value = [
        {"id": 1, "name": "John"},
        {"id": 2, "name": "Jane"}
    ]

    service = UserService(mock_db)
    users = service.get_all_users()

    assert len(users) == 2
    assert users[0]["name"] == "John"


# Spy on real objects
def test_spy(mocker):
    """Test spying on real object"""
    real_dict = {"key": "value"}
    spy = mocker.spy(real_dict, 'get')

    result = real_dict.get("key")

    assert result == "value"
    spy.assert_called_once_with("key")


# Mock assertions
def test_mock_assertions(mocker):
    """Test mock call assertions"""
    mock_func = mocker.Mock()

    mock_func(1, 2, key="value")
    mock_func(3, 4)

    # Assert called
    assert mock_func.called
    assert mock_func.call_count == 2

    # Assert called with
    mock_func.assert_any_call(1, 2, key="value")
    mock_func.assert_any_call(3, 4)

    # Assert call list
    assert mock_func.call_args_list == [
        call(1, 2, key="value"),
        call(3, 4)
    ]


# Mock properties
def test_mock_property(mocker):
    """Test mocking properties"""
    class MyClass:
        @property
        def my_property(self):
            return "real value"

    obj = MyClass()
    mocker.patch.object(
        MyClass,
        'my_property',
        new_callable=PropertyMock,
        return_value="mocked value"
    )

    assert obj.my_property == "mocked value"


# Context manager mocking
def test_mock_context_manager(mocker):
    """Test mocking context manager"""
    mock_open = mocker.mock_open(read_data="file content")
    mocker.patch('builtins.open', mock_open)

    with open('fake_file.txt', 'r') as f:
        content = f.read()

    assert content == "file content"
    mock_open.assert_called_once_with('fake_file.txt', 'r')


# Multiple return values
def test_mock_multiple_returns(mocker):
    """Test mock with multiple return values"""
    mock_func = mocker.Mock()
    mock_func.side_effect = ["first", "second", "third"]

    assert mock_func() == "first"
    assert mock_func() == "second"
    assert mock_func() == "third"


# Async mocking
@pytest.mark.asyncio
async def test_async_mock(mocker):
    """Test async mock"""
    mock_async = mocker.AsyncMock(return_value="async result")
    result = await mock_async()

    assert result == "async result"
    mock_async.assert_called_once()


# Partial mocking
def test_partial_mock(mocker):
    """Test partial mocking with wraps"""
    real_list = [1, 2, 3]
    mock_list = mocker.Mock(wraps=real_list)

    # Real behavior
    assert mock_list[0] == 1

    # But we can track calls
    assert mock_list.__getitem__.call_count == 1


# Mock attributes
def test_mock_attributes(mocker):
    """Test mocking object attributes"""
    mock_obj = mocker.Mock()
    mock_obj.name = "Test"
    mock_obj.value = 42
    mock_obj.items = ["a", "b", "c"]

    assert mock_obj.name == "Test"
    assert mock_obj.value == 42
    assert len(mock_obj.items) == 3


# Fixture with mock
@pytest.fixture
def mock_database(mocker):
    """Mock database fixture"""
    mock_db = mocker.Mock()
    mock_db.fetch_one.return_value = {"id": 1, "name": "Test User"}
    mock_db.fetch_all.return_value = [{"id": 1}, {"id": 2}]
    mock_db.insert.return_value = {"id": 3, "name": "New User"}
    mock_db.delete.return_value = True
    return mock_db


def test_with_mock_fixture(mock_database):
    """Test using mock database fixture"""
    service = UserService(mock_database)

    # Test get user
    user = service.get_user(1)
    assert user["name"] == "Test User"

    # Test get all users
    users = service.get_all_users()
    assert len(users) == 2

    # Test create user
    new_user = service.create_user({"name": "New User"})
    assert new_user["id"] == 3

    # Test delete user
    deleted = service.delete_user(1)
    assert deleted is True


# Reset mock
def test_reset_mock(mocker):
    """Test resetting mock"""
    mock_func = mocker.Mock()
    mock_func(1, 2, 3)
    assert mock_func.call_count == 1

    mock_func.reset_mock()
    assert mock_func.call_count == 0
    assert not mock_func.called
