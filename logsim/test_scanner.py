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
def new_test_scanner_get_symbol():
    """Return a new instance of the Scanner class with predefined path."""
    new_names = Names()
    path = "logsim/test_scanner_get_symbol.txt" # Text file containing scanner tests for get_symbol

    return Scanner(path, new_names)


@pytest.fixture
def new_test_scanner_print_error_line():
    """Return a new instance of the Scanner class with predefined path."""
    new_names = Names()
    path = "logsim/test_scanner_print_error_line.txt" # Text file containing scanner tests for print_error_line

    return Scanner(path, new_names)


def test_scanner_init_raises_exceptions(new_names):
    """Test if Scanner's __init__ method raises expected exceptions."""
    with pytest.raises(TypeError):
        Scanner(9, new_names)
    with pytest.raises(TypeError):
        Scanner(-1.2, new_names)
    with pytest.raises(TypeError):
        Scanner(True, new_names)


def test_get_symbol(new_test_scanner_get_symbol):
    """Test to see if get_symbol returns the correct symbol."""
    scanner = new_test_scanner_get_symbol
    # Skip comment 1
    assert scanner.get_symbol().type == None # Invalid Character
    assert scanner.get_symbol().type == 0 # COMMA
    assert scanner.get_symbol().type == 1 # DOT
    assert scanner.get_symbol().type == 2 # SEMICOLON
    assert scanner.get_symbol().type == 3 # EQUALS
    assert scanner.get_symbol().type == 4 # OPEN_BRACKET
    assert scanner.get_symbol().type == 5 # CLOSE_BRACKET
    assert scanner.get_symbol().type == 7 # NUMBER
    assert scanner.get_symbol().type == 8 # NAME
    # Skip comment 2 and skip spaces + line breaks

    for i in range(30): # KEYWORD
        symbol = scanner.get_symbol()
        assert symbol.type == 6 
        assert symbol.id == i # Correct keyword

    assert scanner.get_symbol().type == None # Invalid Character
    assert scanner.get_symbol().type == 9 # EOF

    # Check further get_symbol still returns EOF
    assert scanner.get_symbol().type == 9 


def test_print_error_line(new_test_scanner_print_error_line):
    scanner = new_test_scanner_print_error_line
    safety_counter = 0
    symbol = scanner.get_symbol()
    print(symbol.type)
    while symbol.type != 9:
        if safety_counter > 10000: # Prevent infinite loop
            break
        print(symbol.type)
        if symbol.type == None:
            scanner.print_error_line("Invalid Character")
            #captured = capsys.readouterr()
        symbol = scanner.get_symbol()
        safety_counter += 1

# Check its passing instance of names class