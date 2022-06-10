"""Test the scanner module."""
import pytest

from final.names import Names
from final.scanner import Scanner, Symbol


@pytest.fixture
def new_names():
    """Return a new instance of the Names class."""
    return Names()


@pytest.fixture
def new_test_scanner():
    """Return a new instance of the Scanner class with predefined path."""
    new_names = Names()
    # Text file containing scanner tests for get_symbol
    path = "final/tests/test_scanner.txt"
    return Scanner(path, new_names)


def test_symbol_init():
    """Test if a Symbol instance is initialised correctly."""
    symbol = Symbol()

    # Check existence
    symbol.id
    symbol.type


def test_scanner_init(new_test_scanner):
    """Test if a Scanner instance is initialised correctly."""
    scanner = new_test_scanner

    # Check existence
    scanner.names
    scanner.symbol_type_list
    scanner.keywords_list
    scanner.current_character
    scanner.current_line
    scanner.current_character_position
    scanner.file
    scanner.lines

    # Check existance of symbol types
    scanner.COMMA
    scanner.DOT
    scanner.SEMICOLON
    scanner.EQUALS
    scanner.OPEN_BRACKET
    scanner.CLOSE_BRACKET
    scanner.KEYWORD
    scanner.NUMBER
    scanner.NAME
    scanner.EOF

    # Check keywords list
    assert scanner.keywords_list == [
        "devices",
        "initialise",
        "connections",
        "monitors",
        "has",
        "have",
        "is",
        "are",
        "to",
        "connected",
        "input",
        "inputs",
        "cycle",
        "length",
        "AND",
        "OR",
        "NOR",
        "XOR",
        "NAND",
        "NOT",
        "DTYPE",
        "SWITCH",
        "CLOCK",
        "HIGH",
        "LOW",
        "DATA",
        "CLK",
        "SET",
        "CLEAR",
        "Q",
        "QBAR"
    ]


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
    scanner = new_test_scanner
    # Skip comment 1
    # Test each symbol type is recognised
    assert scanner.get_symbol().type == scanner.COMMA
    assert scanner.get_symbol().type == scanner.DOT
    assert scanner.get_symbol().type == scanner.SEMICOLON
    assert scanner.get_symbol().type == scanner.EQUALS
    assert scanner.get_symbol().type == scanner.OPEN_BRACKET
    assert scanner.get_symbol().type == scanner.CLOSE_BRACKET
    assert scanner.get_symbol().type == scanner.NUMBER
    assert scanner.get_symbol().type == scanner.NAME
    # Skip comment 2 and skip spaces + line breaks

    for i in range(31):  # Test for keywords
        symbol = scanner.get_symbol()
        assert symbol.type == scanner.KEYWORD
        assert symbol.id == i  # Correct keyword

    # Check the erroneous line
    assert scanner.get_symbol().type == scanner.NAME
    assert scanner.get_symbol().type is None  # Invalid Character
    assert scanner.get_symbol().type == scanner.NAME
    assert scanner.get_symbol().type == scanner.SEMICOLON
    assert scanner.get_symbol().type == scanner.DOT

    # Check end of file is reached
    assert scanner.get_symbol().type == scanner.EOF

    # Check further get_symbol calls still return EOF
    assert scanner.get_symbol().type == scanner.EOF


def test_print_error_line(new_test_scanner, capsys):
    """Test to see that print_error_line prints error markers correctly."""
    scanner = new_test_scanner
    safety_counter = 0
    symbol = scanner.get_symbol()

    while symbol.type != scanner.EOF:
        if safety_counter > 10000:  # Prevent infinite loop
            break
        # Search for invalid character
        if symbol.type is None:
            scanner.print_error_line(symbol.line_number, symbol.line_position,
                                     "Invalid Character")
            captured = capsys.readouterr()

            # Test that pointer "^" lies directly underneath invalid character
            current_line = 0
            current_character_location = -1
            invalid_character_location = -1
            error_pointer_location = -1
            for letter in captured.out:
                if current_line == 1:
                    current_character_location += 1
                    if letter == "-":
                        invalid_character_location = current_character_location

                elif current_line == 2:
                    current_character_location += 1
                    if letter == "^":
                        error_pointer_location = current_character_location

                if letter == "\n":
                    current_line += 1
                    current_character_location = -1

            assert invalid_character_location == 5  # Location of "-"
            assert error_pointer_location == 5  # Location of "^"

        symbol = scanner.get_symbol()
        safety_counter += 1
