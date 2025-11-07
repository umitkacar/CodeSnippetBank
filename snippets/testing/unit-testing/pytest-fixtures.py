"""
Pytest Advanced Fixtures
Comprehensive fixture patterns and best practices
"""

import pytest
from typing import Generator, Dict, List


# Basic fixtures
@pytest.fixture
def sample_user() -> Dict[str, any]:
    """Fixture providing a sample user"""
    return {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "active": True
    }


@pytest.fixture
def sample_users() -> List[Dict[str, any]]:
    """Fixture providing multiple users"""
    return [
        {"id": 1, "name": "John Doe", "email": "john@example.com"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
        {"id": 3, "name": "Bob Johnson", "email": "bob@example.com"},
    ]


# Fixture with setup/teardown
@pytest.fixture
def database_connection():
    """Fixture with setup and teardown"""
    # Setup
    connection = {"connected": True, "data": {}}
    print("\nSetting up database connection")

    yield connection

    # Teardown
    print("\nClosing database connection")
    connection["connected"] = False


# Fixture scope examples
@pytest.fixture(scope="function")
def function_scope_fixture():
    """Function scope - runs for each test function"""
    return {"scope": "function"}


@pytest.fixture(scope="class")
def class_scope_fixture():
    """Class scope - runs once per test class"""
    return {"scope": "class"}


@pytest.fixture(scope="module")
def module_scope_fixture():
    """Module scope - runs once per module"""
    return {"scope": "module"}


@pytest.fixture(scope="session")
def session_scope_fixture():
    """Session scope - runs once per test session"""
    return {"scope": "session", "counter": 0}


# Parametrized fixtures
@pytest.fixture(params=[1, 2, 3, 4, 5])
def number_fixture(request):
    """Parametrized fixture"""
    return request.param


@pytest.fixture(params=["sqlite", "postgresql", "mysql"])
def database_type(request):
    """Parametrized database type"""
    return request.param


# Fixture factories
@pytest.fixture
def user_factory():
    """Fixture factory for creating users"""
    def _create_user(name: str, email: str):
        return {
            "id": hash(email) % 10000,
            "name": name,
            "email": email,
            "active": True
        }
    return _create_user


# Fixture with autouse
@pytest.fixture(autouse=True)
def reset_state():
    """Auto-use fixture that runs for every test"""
    global _state
    _state = {}
    yield
    _state = {}


_state = {}


# Fixture depending on other fixtures
@pytest.fixture
def user_with_posts(sample_user):
    """Fixture depending on another fixture"""
    sample_user["posts"] = [
        {"id": 1, "title": "First Post", "content": "Hello World"},
        {"id": 2, "title": "Second Post", "content": "Testing"},
    ]
    return sample_user


# Temporary directory fixture
@pytest.fixture
def temp_dir(tmp_path):
    """Fixture using pytest's tmp_path"""
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()
    return test_dir


# Mock configuration fixture
@pytest.fixture
def app_config():
    """Application configuration fixture"""
    return {
        "debug": True,
        "database_url": "sqlite:///:memory:",
        "secret_key": "test-secret-key",
        "api_timeout": 30,
    }


# Tests using fixtures
def test_user_fixture(sample_user):
    """Test using sample user fixture"""
    assert sample_user["name"] == "John Doe"
    assert sample_user["active"] is True


def test_users_fixture(sample_users):
    """Test using multiple users fixture"""
    assert len(sample_users) == 3
    assert sample_users[0]["name"] == "John Doe"


def test_database_connection(database_connection):
    """Test database connection fixture"""
    assert database_connection["connected"] is True
    database_connection["data"]["test"] = "value"
    assert database_connection["data"]["test"] == "value"


def test_parametrized_fixture(number_fixture):
    """Test with parametrized fixture"""
    assert number_fixture >= 1
    assert number_fixture <= 5


def test_user_factory(user_factory):
    """Test user factory fixture"""
    user1 = user_factory("Alice", "alice@example.com")
    user2 = user_factory("Bob", "bob@example.com")

    assert user1["name"] == "Alice"
    assert user2["name"] == "Bob"
    assert user1["id"] != user2["id"]


def test_fixture_composition(user_with_posts):
    """Test fixture depending on other fixtures"""
    assert "posts" in user_with_posts
    assert len(user_with_posts["posts"]) == 2
    assert user_with_posts["posts"][0]["title"] == "First Post"


def test_temp_directory(temp_dir):
    """Test temporary directory fixture"""
    test_file = temp_dir / "test.txt"
    test_file.write_text("Hello, World!")
    assert test_file.read_text() == "Hello, World!"


def test_app_config(app_config):
    """Test application config fixture"""
    assert app_config["debug"] is True
    assert app_config["api_timeout"] == 30


# Fixture with request parameter
@pytest.fixture
def parametrized_config(request):
    """Fixture using request parameter"""
    config = {"env": "test"}
    if hasattr(request, "param"):
        config.update(request.param)
    return config


@pytest.mark.parametrize("parametrized_config", [
    {"debug": True},
    {"debug": False},
], indirect=True)
def test_indirect_parametrization(parametrized_config):
    """Test with indirect parametrization"""
    assert "env" in parametrized_config
    assert "debug" in parametrized_config
