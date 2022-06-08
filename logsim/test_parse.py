"""Test the parse module."""
import pytest
from names import Names
from string_scanner import Scanner, Symbol
from monitors import Monitors
from devices import Devices
from network import Network
from string_parser import Parser
from global_vars import GlobalVars
# Syntax errors
from error import (
    InvalidBlockHeaderOrder,
    ParserError,
    InvalidBlockHeader,
    RedefinedError,
    SemicolonError,
    OpenBracketError,
    CloseBracketError,
    InvalidDeviceRule,
    InvalidInitDeviceRule,
    InvalidInitSwitchRule,
    InvalidInitClockRule,
    DeviceTypeError,
    InvalidDeviceName,
    InvalidClockName,
    InvalidSwitchName,
    InvalidSwitchState,
    InputNumberMissing,
    InputsDefinedIncorrectly,
    ConnectedToError,
    OutputPortError,
    InputPortError,
    DotError,
    ExtraInfoAfterMonitors
)

def new_objects(string):
    """Return a new instance of all classes"""
    global_vars = GlobalVars()
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    scanner = Scanner(names, string)
    parser = Parser(names, devices, network, monitors, scanner, global_vars)
    return names, devices, network, monitors, scanner, parser

@pytest.mark.parametrize("string,error", [("\na is OR;\n)", OpenBracketError),
                        ("(\na is OR;\n", CloseBracketError)])
def test_devices_block(string, error):
    names, devices, network, monitors, scanner, parser = new_objects(string)
    symbol = Symbol()
    # Create mock symbol to pass into devices block
    [symbol.id] = names.lookup(["devices"])
    symbol.type = scanner.KEYWORD
    with pytest.raises(error):
        parser.devices_block(symbol)

@pytest.mark.parametrize("string,error", [("(\n1 is OR;\n)", ParserError),
                        ("(\na is AND;\na is OR;)", RedefinedError),
                        ("(\na is APPLE;\n)", DeviceTypeError),
                        ("(\na is AND\n)", SemicolonError),
                        ("(\na has AND\n)", InvalidDeviceRule)])
def test_devices_subrule(string, error):
    names, devices, network, monitors, scanner, parser = new_objects(string)
    symbol = Symbol()
    # Create mock symbol to pass into devices block
    [symbol.id] = names.lookup(["devices"])
    symbol.type = scanner.KEYWORD
    parser.devices_block(symbol)
    for i in parser.syntax_errors:
        assert isinstance (i, error)

@pytest.mark.parametrize("string,error", [("initialise(\na has 2 inputs;\n)\ndevices(\na is OR;\n)", InvalidBlockHeaderOrder),
                        ("devices\n(a is AND;\n)\ninitialise(\na has 2 inputs;\n)\nconnections(\n)\nmonitors(\na;\n)\nveni vidi vici", ExtraInfoAfterMonitors),
                        ("devices(\na is OR;\n)\njabberwocky(\na has 2 inputs;\n)\nconnections(\n)\nmonitors(\n)", InvalidBlockHeader)])
def test_block_order(string, error):
    names, devices, network, monitors, scanner, parser = new_objects(string)
    parser.parse_network()
    assert any(isinstance(i, error) for i in parser.syntax_errors) 