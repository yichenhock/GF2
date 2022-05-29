"""Test the scanner module."""
import pytest

from names import Names
from scanner import Scanner, Symbol


@pytest.fixture
def new_names():
    """Return a new instance of the Names class."""
    return Names()


@pytest.fixture
def new_test_scanner(new_names):
    """Return a new instance of the Scanner class with predefined path."""
    path = "test_scanner.txt" # Text file containing scanner tests
    return Scanner(path, new_names)


def test_scanner_init_raises_exceptions(new_test_scanner(new_names)):
    """Test if Scanner's __init__ method raises expected exceptions."""
