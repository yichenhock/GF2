"""Test the scanner module."""
import pytest

from names import Names
from scanner import Scanner, Symbol
import os


@pytest.fixture
def new_names():
    """Return a new instance of the Names class."""
    return Names()


@pytest.fixture
def new_test_scanner():
    """Return a new instance of the Scanner class with predefined path."""
    new_names = Names()
    path = "logsim/test_scanner.txt" # Text file containing scanner tests

    return Scanner(path, new_names)


def test_scanner_init_raises_exceptions(new_names):
    """Test if Scanner's __init__ method raises expected exceptions."""
    with pytest.raises(TypeError):
        Scanner(9, new_names)
    with pytest.raises(TypeError):
        Scanner(-1.2, new_names)
    with pytest.raises(TypeError):
        Scanner(True, new_names)


def test_get_symbol(new_test_scanner):
    """Test to see if get_symbol returns the correct symbol."""
    pass

def test_print_error_line(new_test_scanner):
    pass



#Check its passing instance of names class