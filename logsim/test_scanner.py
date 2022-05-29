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
    print(new_test_scanner.devices_id)
    # Skip comment 1
    assert new_test_scanner.get_symbol().type == None # Invalid Character
    assert new_test_scanner.get_symbol().type == 0 # COMMA
    assert new_test_scanner.get_symbol().type == 1 # DOT
    assert new_test_scanner.get_symbol().type == 2 # SEMICOLON
    assert new_test_scanner.get_symbol().type == 3 # EQUALS
    assert new_test_scanner.get_symbol().type == 4 # OPEN_BRACKET
    assert new_test_scanner.get_symbol().type == 5 # CLOSE_BRACKET
    assert new_test_scanner.get_symbol().type == 7 # NUMBER
    # Skip comment 2
    assert new_test_scanner.get_symbol().type == 8 # NAME
    

    for i in range(30): # KEYWORD
        print(i)
        assert new_test_scanner.get_symbol().type == 6 
        assert new_test_scanner.get_symbol().id == i # Invalid Character

    assert new_test_scanner.get_symbol().type == 9 # Invalid Character

def test_print_error_line(new_test_scanner):
    pass



#Check its passing instance of names class