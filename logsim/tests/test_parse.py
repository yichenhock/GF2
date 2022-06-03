"""Test the parse module."""
import pytest

from logsim.names import Names
from logsim.scanner import Scanner, Symbol

from logsim.monitors import Monitors
from logsim.devices import Devices
from logsim.network import Network
from logsim.parse import Parser

from logsim.error import SyntaxError, SemanticError

@pytest.fixture
def new_names():
    """Return a new instance of the Names class."""
    return Names()

# @pytest.fixture
# def new_test_scanner():
#     """Return a new instance of the Scanner class with predefined path."""
#     new_names = Names()
#     # Text file containing scanner tests for get_symbol
#     path = "logsim/tests/test_scanner.txt"
#     return Scanner(path, new_names)

def test_no_open_bracket():

    "devices"

    assert SyntaxError.NO_OPEN_BRACKET

