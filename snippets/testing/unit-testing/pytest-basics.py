"""
Pytest Basic Testing Patterns
Comprehensive pytest examples and best practices
"""

import pytest


# Basic test functions
def test_addition():
    """Test basic addition"""
    assert 2 + 2 == 4


def test_subtraction():
    """Test basic subtraction"""
    assert 5 - 3 == 2


def test_multiplication():
    """Test basic multiplication"""
    assert 3 * 4 == 12


def test_division():
    """Test basic division"""
    assert 10 / 2 == 5


# Testing exceptions
def test_division_by_zero():
    """Test division by zero raises exception"""
    with pytest.raises(ZeroDivisionError):
        1 / 0


def test_exception_message():
    """Test exception with specific message"""
    with pytest.raises(ValueError, match="invalid literal"):
        int("not a number")


# Parameterized tests
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (5, 5, 10),
    (10, -5, 5),
    (0, 0, 0),
])
def test_parameterized_addition(a, b, expected):
    """Test addition with multiple parameters"""
    assert a + b == expected


@pytest.mark.parametrize("value,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("PyTest", "PYTEST"),
])
def test_string_upper(value, expected):
    """Test string upper case conversion"""
    assert value.upper() == expected


# Fixtures
@pytest.fixture
def sample_data():
    """Fixture providing sample data"""
    return {"name": "John", "age": 30, "city": "New York"}


@pytest.fixture
def sample_list():
    """Fixture providing sample list"""
    return [1, 2, 3, 4, 5]


def test_with_fixture(sample_data):
    """Test using fixture"""
    assert sample_data["name"] == "John"
    assert sample_data["age"] == 30


def test_list_fixture(sample_list):
    """Test list fixture"""
    assert len(sample_list) == 5
    assert 3 in sample_list


# Setup and teardown
class TestWithSetup:
    """Test class with setup and teardown"""

    def setup_method(self):
        """Setup before each test method"""
        self.counter = 0

    def teardown_method(self):
        """Teardown after each test method"""
        self.counter = 0

    def test_increment(self):
        """Test increment"""
        self.counter += 1
        assert self.counter == 1

    def test_counter_starts_at_zero(self):
        """Test counter initial value"""
        assert self.counter == 0


# Testing classes
class Calculator:
    """Simple calculator class"""

    def add(self, a: int, b: int) -> int:
        return a + b

    def subtract(self, a: int, b: int) -> int:
        return a - b

    def multiply(self, a: int, b: int) -> int:
        return a * b

    def divide(self, a: int, b: int) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b


@pytest.fixture
def calculator():
    """Fixture providing calculator instance"""
    return Calculator()


class TestCalculator:
    """Test calculator class"""

    def test_add(self, calculator):
        """Test addition"""
        assert calculator.add(2, 3) == 5

    def test_subtract(self, calculator):
        """Test subtraction"""
        assert calculator.subtract(10, 5) == 5

    def test_multiply(self, calculator):
        """Test multiplication"""
        assert calculator.multiply(3, 4) == 12

    def test_divide(self, calculator):
        """Test division"""
        assert calculator.divide(10, 2) == 5

    def test_divide_by_zero(self, calculator):
        """Test division by zero"""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            calculator.divide(10, 0)


# Markers
@pytest.mark.slow
def test_slow_operation():
    """Test marked as slow"""
    import time
    time.sleep(0.1)
    assert True


@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    """Test to be implemented"""
    pass


@pytest.mark.skipif(True, reason="Conditional skip")
def test_conditional():
    """Conditionally skipped test"""
    assert False


@pytest.mark.xfail
def test_expected_failure():
    """Test expected to fail"""
    assert False
