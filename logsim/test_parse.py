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

# Semantic errors
from error import (
    UndefinedError,
    RedefinedError,
    WrongDeviceName,
    WrongSwitchName,
    WrongClockName,
    InvalidClockLength,
    InvalidInputNumber,
    AttemptToDefineXORInputs,
    AttemptToDefineNOTInputs,
    AttemptToDefineDTYPEInputs,
    NoDTYPEOutputPortError,
    InvalidBlockHeaderOrder,
    DeviceNotInitialised,
    SwitchNotInitialised,
    ClockNotInitialised,
    NotInitialisedError,
    ConnectionPresent
)

@pytest.fixture(scope='function')
def new_scanner(request):
    names = Names()
    return names, Scanner(names, request.param)

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

@pytest.mark.parametrize("string,error", [("initialise(\na has 2 inputs;\n)\ndevices(\na is OR;\n)", InvalidBlockHeaderOrder),
                        ("devices\n(a is AND;\n)\ninitialise(\na has 2 inputs;\n)\nconnections(\n)\nmonitors(\na;\n)\nveni vidi vici", ExtraInfoAfterMonitors),
                        ("devices(\na is OR;\n)\njabberwocky(\na has 2 inputs;\n)\nconnections(\n)\nmonitors(\n)", InvalidBlockHeader)])
def test_block_order(string, error):
    names, devices, network, monitors, scanner, parser = new_objects(string)
    parser.parse_network()
    errors = parser.syntax_errors + parser.semantic_errors
    assert any(isinstance(i, error) for i in errors) 

@pytest.mark.parametrize("string,error", [("\na is OR;\n)", OpenBracketError),
                        ("(\na is OR;\n", CloseBracketError)])
def test_devices_block(string, error):
    """Test whether devices_block() returns the correct errors."""
    names, devices, network, monitors, scanner, parser = new_objects(string)
    symbol = Symbol()
    # Create mock symbol to pass into devices block
    [symbol.id] = names.lookup(["devices"])
    symbol.type = scanner.KEYWORD
    with pytest.raises(error):
        parser.devices_block(symbol)

# Also tests check_name_legal()
@pytest.mark.parametrize("string,error", [("(\n1 is OR;\n)", InvalidDeviceName),

                        ("(\na is AND;\na is OR;)", RedefinedError),

                        ("(\na is GROOT;\n)", DeviceTypeError),

                        ("(\na is AND\n)", SemicolonError),

                        ("(\na has AND;\n)", InvalidDeviceRule),

                        ("(\nswitch is SWITCH;\n)", WrongSwitchName),

                        ("(\na is SWITCH;\n)", WrongSwitchName),

                        ("(\nclock is CLOCK;\n)", WrongClockName),

                        ("(\na is CLOCK;\n)", WrongClockName),

                        ("(\nsw1 is AND;\n)", WrongDeviceName)])
def test_devices_subrule(string, error):
    """Test whether devices_subrule() and check_name_legal() return the correct errors."""
    names, devices, network, monitors, scanner, parser = new_objects(string)
    symbol = Symbol()
    # Create mock symbol to pass into devices block
    [symbol.id] = names.lookup(["devices"])
    symbol.type = scanner.KEYWORD
    parser.devices_block(symbol)
    errors = parser.syntax_errors + parser.semantic_errors
    assert any(isinstance(i, error) for i in errors) 

@pytest.mark.parametrize("string,error", [("devices\n(a is AND;\n)\ninitialise(\n1 has 2 inputs;\n)\nconnections(\n)\nmonitors(\na;\n)", InvalidDeviceName),

                        ("devices\n(a is AND;\n)\ninitialise(\nb has 2 inputs;\n)\nconnections(\n)\nmonitors(\na;\n)", UndefinedError),

                        ("devices\n(sw1 is SWITCH;\n)\ninitialise(\nsw1 is PINGU;\n)\nconnections(\n)\nmonitors(\nsw1;\n)", InvalidSwitchState),

                        ("devices\n(sw1 is SWITCH;\n)\ninitialise(\nsw1 is HIGH\n)\nconnections(\n)\nmonitors(\nsw1;\n)", SemicolonError),

                        ("devices\n(a is NAND;\n)\ninitialise(\na has 2 inputs\n)\nconnections(\n)\nmonitors(\na;\n)", SemicolonError),

                        ("devices\n(clk1 is CLOCK;\n)\ninitialise(\nclk1 cycle length 10\n)\nconnections(\n)\nmonitors(\nclk1;\n)", SemicolonError),

                        ("devices\n(sw1 is SWITCH;\n)\ninitialise(\nsw1 got HIGH;\n)\nconnections(\n)\nmonitors(\nsw1;\n)", InvalidInitSwitchRule),
                        
                        ("devices\n(clk1 is CLOCK;\n)\ninitialise(\nclk1 cycle length infinity;\n)\nconnections(\n)\nmonitors(\nclk1;\n)", InvalidClockLength),

                        ("devices\n(clk1 is CLOCK;\n)\ninitialise(\nclk1 cuckoo length 10;\n)\nconnections(\n)\nmonitors(\nclk1;\n)", InvalidInitClockRule),

                        ("devices\n(a is DTYPE;\n)\ninitialise(\na has 4 inputs;\n)\nconnections(\n)\nmonitors(\na;\n)", AttemptToDefineDTYPEInputs),

                        ("devices\n(a is XOR;\n)\ninitialise(\na has 2 inputs;\n)\nconnections(\n)\nmonitors(\na;\n)", AttemptToDefineXORInputs),

                        ("devices\n(a is NOT;\n)\ninitialise(\na has 1 input;\n)\nconnections(\n)\nmonitors(\na;\n)", AttemptToDefineNOTInputs),

                        ("devices\n(a is NAND;\n)\ninitialise(\na has 42 inputs;\n)\nconnections(\n)\nmonitors(\na;\n)", InvalidInputNumber),

                        ("devices\n(henry is NAND;\n)\ninitialise(\nhenry has 6 wives;\n)\nconnections(\n)\nmonitors(\nhenry;\n)", InputsDefinedIncorrectly),

                        ("devices\n(a is NAND;\n)\ninitialise(\na has n inputs;\n)\nconnections(\n)\nmonitors(\na;\n)", InputNumberMissing),

                        ("devices\n(a is NAND;\n)\ninitialise(\na takes 2 inputs;\n)\nconnections(\n)\nmonitors(\na;\n)", InvalidInitDeviceRule),

                        ("devices\n(b is NAND;\n)\ninitialise(\na has 2 inputs;\n)\nconnections(\n)\nmonitors(\na;\n)", DeviceNotInitialised)])
def test_initialise_block(string, error):
    """Test whether initialise_block(), initialise_subrule(), init_switch(), init_clock() and init_gate() return the correct errors."""
    names, devices, network, monitors, scanner, parser = new_objects(string)
    parser.parse_network()
    errors = parser.syntax_errors + parser.semantic_errors
    assert any(isinstance(i, error) for i in errors)  

@pytest.mark.parametrize("string,error", [("devices\n(sw1 is SWITCH;\n)\ninitialise(\n)\nconnections(\n)\nmonitors(\nsw1;\n)", SwitchNotInitialised),

                        ("devices\n(sw1 is SWITCH;\n)\ninitialise(\n)\nconnections(\n)\nmonitors(\nsw1;\n)", NotInitialisedError),

                        ("devices\n(clk1 is CLOCK;\n)\ninitialise(\n)\nconnections(\n)\nmonitors(\nclk1;\n)", ClockNotInitialised),

                        ("devices\n(a is AND;\n)\ninitialise(\n)\nconnections(\n)\nmonitors(\nclk1;\n)", DeviceNotInitialised),
                        ])
def test_make_devices(string, error):
    """Test whether make_devices() returns the correct errors."""
    names, devices, network, monitors, scanner, parser = new_objects(string)
    parser.parse_network()
    assert any(isinstance(i, error) for i in parser.not_initialised_errors) 

@pytest.mark.parametrize("string,error", [("devices\n(a is AND;\nsw1 is SWITCH;\nsw2 is SWITCH;\n)\ninitialise(\na has 2 inputs;\nsw1 is HIGH;\nsw2 is LOW;\n)\nconnections(\nsw1 pontificates a.I1;\n)\nmonitors(\na;\n)", ConnectedToError),

                        ("devices\n(a is AND;\nsw1 is SWITCH;\nsw2 is SWITCH;\n)\ninitialise(\na has 2 inputs;\nsw1 is HIGH;\nsw2 is LOW;\n)\nconnections(\nsw1 is flagellated by a.I1;\n)\nmonitors(\na;\n)", ConnectedToError),

                        ("devices\n(a is AND;\nsw1 is SWITCH;\nsw2 is SWITCH;\n)\ninitialise(\na has 2 inputs;\nsw1 is HIGH;\nsw2 is LOW;\n)\nconnections(\nsw1 is connected by a.I1;\n)\nmonitors(\na;\n)", ConnectedToError),

                        ("devices\n(a is AND;\nsw1 is SWITCH;\nsw2 is SWITCH;\n)\ninitialise(\na has 2 inputs;\nsw1 is HIGH;\nsw2 is LOW;\n)\nconnections(\nsw1 to a.I1\n)\nmonitors(\na;\n)", SemicolonError),

                        ("devices\n(a is AND;\nsw1 is SWITCH;\nsw2 is SWITCH;\n)\ninitialise(\na has 2 inputs;\nsw1 is HIGH;\nsw2 is LOW;\n)\nconnections(\n1 to a.I1\n)\nmonitors(\na;\n)", InvalidDeviceName),

                        ("devices\n(a is AND;\nsw1 is SWITCH;\nsw2 is SWITCH;\n)\ninitialise(\na has 2 inputs;\nsw1 is HIGH;\nsw2 is LOW;\n)\nconnections(\ncheshire to a.I1\n)\nmonitors(\na;\n)", UndefinedError),

                        ("devices\n(a is DTYPE;\nb is AND;\nsw1 is SWITCH;\nsw2 is SWITCH;\n)\ninitialise(\nsw1 is HIGH;\nsw2 is LOW;\n)\nconnections(\na to b.I1;\n)\nmonitors(\na;\n)", NoDTYPEOutputPortError),

                        ("devices\n(a is DTYPE;\nb is AND;\nsw1 is SWITCH;\nsw2 is SWITCH;\n)\ninitialise(\nsw1 is HIGH;\nsw2 is LOW;\n)\nconnections(\na.EVERGREEN to b.I1;\n)\nmonitors(\na;\n)", OutputPortError),

                        ("devices\n(a is AND;\nsw1 is SWITCH;\nsw2 is SWITCH;\n)\ninitialise(\na has 2 inputs;\nsw1 is HIGH;\nsw2 is LOW;\n)\nconnections(\nsw1 to a.I3;\n)\nmonitors(\na;\n)", InputPortError),

                        ("devices\n(a is AND;\nsw1 is SWITCH;\nsw2 is SWITCH;\n)\ninitialise(\na has 2 inputs;\nsw1 is HIGH;\nsw2 is LOW;\n)\nconnections(\nsw1 to 1.I1;\n)\nmonitors(\na;\n)", InvalidDeviceName),

                        ("devices\n(a is AND;\nsw1 is SWITCH;\nsw2 is SWITCH;\n)\ninitialise(\na has 2 inputs;\nsw1 is HIGH;\nsw2 is LOW;\n)\nconnections(\nsw1 to cheshire.I1;\n)\nmonitors(\na;\n)", UndefinedError),

                        ("devices\n(a is AND;\nsw1 is SWITCH;\nsw2 is SWITCH;\n)\ninitialise(\na has 2 inputs;\nsw1 is HIGH;\nsw2 is LOW;\n)\nconnections(\nsw1 to a;\n)\nmonitors(\na;\n)", DotError),

                        ("devices\n(a is AND;\nsw1 is SWITCH;\nsw2 is SWITCH;\n)\ninitialise(\na has 2 inputs;\nsw1 is HIGH;\nsw2 is LOW;\n)\nconnections(\nsw1 to a.I1,\nsw2 to a.I1;\n)\nmonitors(\na;\n)", ConnectionPresent),
                        ]) 
def test_connections_block(string, error):
    """Test whether connections_block(), connections_subrule(), parse_output_rule(), parse_input_rule(), is_output_port, is_input_port and make_connections() return the correct errors."""
    names, devices, network, monitors, scanner, parser = new_objects(string)
    parser.parse_network()
    for i in parser.syntax_errors:
        assert any(isinstance(i, error) for i in parser.syntax_errors) 

@pytest.mark.parametrize("new_scanner", [("Test \n scanner;\n 123")], indirect=True)
def test_string_scanner(new_scanner):
    names, scanner = new_scanner
    sym = scanner.get_symbol()
    while scanner.current_character != "":
        if sym.type == scanner.NUMBER:
            assert sym.id == 123
        sym = scanner.get_symbol()
    assert "Test" in names.names
    assert "scanner" in names.names