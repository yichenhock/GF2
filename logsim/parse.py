"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""

from names import Names
from scanner import Symbol, Scanner
from devices import Device, Devices
from network import Network
from monitors import Monitors

from error import ParserError, ParserSemanticError, ParserSyntaxError

# Semantic errors
from error import (
    UndefinedError,
    RedefinedError,
    WrongDeviceName,
    WrongSwitchName,
    WrongClockName,
    InvalidClockLength,
    InvalidInputNumber,
    InvalidXORInputNumber,
    InvalidNOTInputNumber,
    AttemptToDefineDTYPEInputs,
    NoDTYPEOutputPortError,
    InvalidBlockHeaderOrder
)

# Syntax errors
from error import (
    InvalidBlockHeader,
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
    DotError
)


class Parser:

    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""

        # names class object
        self.names = names
        self.devices = devices
        self.network = network
        self.scanner = scanner
        self.monitors = monitors

        self.in_block = False  # True if parser inside a block

        self.syntax_errors = []
        self.semantic_errors = []
        self.input_not_connected_errors = []

        self.names_parsed = []

        self.device_dict = {}  # {device_id: device_kind, device_property=None}

        # [(input_id_symbol, input_port_id_symbol), ...]
        self.input_symbols = []
        self.output_symbol = None  # (output_id_symbol, output_port_id_symbol)

        self.monitor_symbols = []  # all symbols that can possibly be monitored

    def devices_block(self, symbol):
        """Check if symbols form a device block.

        """
        next_sym = self.scanner.get_symbol()

        if next_sym.type == self.scanner.OPEN_BRACKET:
            self.in_block = True
            next_sym = self.scanner.get_symbol()
            while next_sym.type != self.scanner.CLOSE_BRACKET:
                if next_sym.type == self.scanner.EOF:
                    # raise a close bracket error
                    raise CloseBracketError(next_sym)
                next_sym = self.devices_subrule(next_sym)
            self.in_block = False
            next_sym = self.scanner.get_symbol()
        else:
            raise OpenBracketError(next_sym)  # raise open bracket error
        return next_sym

    def devices_subrule(self, symbol):
        try:
            connect = [self.scanner.is_id, self.scanner.are_id]
            types = [self.scanner.AND_id,
                     self.scanner.OR_id,
                     self.scanner.NOR_id,
                     self.scanner.XOR_id,
                     self.scanner.NOT_id,
                     self.scanner.NAND_id,
                     self.scanner.DTYPE_id,
                     self.scanner.SWITCH_id,
                     self.scanner.CLOCK_id]
            name_symbols = []
            checking_devices = True

            while checking_devices:
                if symbol.type == self.scanner.NAME:

                    if self.names.get_name_string(symbol.id) in \
                            self.names_parsed:
                        raise RedefinedError(
                            symbol, self.names.get_name_string(symbol.id))
                    else:
                        self.names_parsed.append(
                            self.names.get_name_string(symbol.id))
                        name_symbols.append(symbol)

                    # now expect either 'IS/ARE' or 'COMMA, NAME'
                    symbol = self.scanner.get_symbol()

                    if symbol.id in connect:  # go to detect the device!
                        checking_devices = False
                        symbol = self.scanner.get_symbol()
                        if symbol.id in types:
                            # first check if the names are legal
                            for name_symbol in name_symbols:
                                self.check_name_legal(name_symbol, symbol.id)
                                # add to devices for connecting up later
                                # devices can only be connected after
                                # initialise block
                                self.device_dict[name_symbol.id] = {
                                    'type': symbol.id,
                                    'property': None
                                }
                        else:
                            # expected a device type
                            raise DeviceTypeError(symbol)

                        symbol = self.scanner.get_symbol()
                        if symbol.type != self.scanner.SEMICOLON:
                            raise SemicolonError(symbol)

                    elif symbol.type == self.scanner.COMMA:
                        symbol = self.scanner.get_symbol()

                    else:
                        checking_devices = False
                        # invalid device subrule statement
                        raise InvalidDeviceRule(symbol)
                else:
                    checking_devices = False
                    # expected a valid device name
                    raise InvalidDeviceName(symbol)

            next_sym = self.scanner.get_symbol()

        except ParserError as e:
            self.add_error(e)
            next_sym = self.skip_error(e)

        return next_sym

    def check_name_legal(self, name_symbol, component_type):
        name = self.names.get_name_string(name_symbol.id)
        if not name.islower():  # device names have to be all lower case
            return False
        if component_type == self.scanner.SWITCH_id:
            # check if the name of the device is the right syntax for a switch
            if not self.is_switch_legal(name):
                raise WrongSwitchName(name_symbol, name)
        elif component_type == self.scanner.CLOCK_id:
            # check if the name of the device is the right syntax for a clock
            if not self.is_clock_legal(name):
                raise WrongClockName(name_symbol, name)
        else:
            if self.is_switch_legal(name) or self.is_clock_legal(name):
                raise WrongDeviceName(name_symbol, name)

    def is_switch_legal(self, name):
        # returns true if name starts with 'sw' followed by a number or nothing
        if len(name) == 2:
            if name == 'sw':
                return True
        elif len(name) > 2:
            if name[:2] == 'sw':
                if name[2:].isnumeric():
                    return True
                else:
                    return False
            else:
                return False

    def is_clock_legal(self, name):
        # returns true if name starts with 'clk' followed
        # by a number or nothing
        if len(name) == 3:
            if name == 'clk':
                return True
        elif len(name) > 3:
            if name[:3] == 'clk':
                if name[3:].isnumeric():
                    return True
                else:
                    return False
            else:
                return False

# =============================================================================
# =============================================================================

    def initialise_block(self, symbol):
        """Check if symbols form a initialise block.

        """

        next_sym = self.scanner.get_symbol()

        if next_sym.type == self.scanner.OPEN_BRACKET:
            self.in_block = True
            next_sym = self.scanner.get_symbol()
            while next_sym.type != self.scanner.CLOSE_BRACKET:
                if next_sym.type == self.scanner.EOF:
                    # raise a close bracket error
                    raise CloseBracketError(next_sym)
                next_sym = self.initialise_subrule(next_sym)
            self.in_block = False
            next_sym = self.scanner.get_symbol()
        else:
            raise OpenBracketError(next_sym)  # raise open bracket error
        self.make_devices()
        return next_sym

    def initialise_subrule(self, symbol):
        try:
            if symbol.type == self.scanner.NAME:
                if symbol.id in self.device_dict:
                    device_type = self.device_dict[symbol.id]['type']
                    # if device is a switch
                    if device_type == self.scanner.SWITCH_id:
                        next_sym = self.init_switch(symbol)
                    # if device is a clock
                    elif device_type == self.scanner.CLOCK_id:
                        next_sym = self.init_clock(symbol)
                    # if device is a gate
                    else:
                        next_sym = self.init_gate(symbol)
                else:
                    raise UndefinedError(
                        symbol, self.names.get_name_string(symbol.id))
            else:
                raise InvalidDeviceName(symbol)

            next_sym = self.scanner.get_symbol()

        except ParserError as e:
            self.add_error(e)
            next_sym = self.skip_error(e)

        return next_sym

    def init_switch(self, symbol):
        next_sym = symbol
        connect = [self.scanner.is_id, self.scanner.are_id]
        checking_devices = True
        device_symbols = []
        while checking_devices:
            if next_sym.type != self.scanner.NAME:
                raise InvalidDeviceName(next_sym)

            device_name = self.names.get_name_string(next_sym.id)
            if next_sym.id not in self.device_dict:
                raise UndefinedError(next_sym, device_name)

            device_type = self.device_dict[next_sym.id]['type']
            if device_type != self.scanner.SWITCH_id:
                raise InvalidSwitchName(next_sym, device_name)

            device_symbols.append(next_sym)

            next_sym = self.scanner.get_symbol()
            # next one is either a connection word or a comma
            if next_sym.id in connect:
                checking_devices = False
                # next word has to be HIGH/LOW
                next_sym = self.scanner.get_symbol()
                if next_sym.id in [self.scanner.HIGH_id, self.scanner.LOW_id]:
                    if next_sym.id == self.scanner.HIGH_id:
                        state = 1
                    else:
                        state = 0
                    # edit the device property for making devices later
                    for sym in device_symbols:
                        self.device_dict[sym.id]['property'] = state
                else:
                    raise InvalidSwitchState(next_sym)

                next_sym = self.scanner.get_symbol()
                if next_sym.type != self.scanner.SEMICOLON:
                    raise SemicolonError(next_sym)

            elif next_sym.type == self.scanner.COMMA:
                next_sym = self.scanner.get_symbol()

            else:
                checking_devices = False
                raise InvalidInitSwitchRule(next_sym)

        return next_sym

    def init_clock(self, symbol):
        next_sym = symbol
        connect = [self.scanner.cycle_id]
        checking_devices = True
        device_symbols = []
        while checking_devices:
            if next_sym.type != self.scanner.NAME:
                raise InvalidDeviceName(next_sym)

            device_name = self.names.get_name_string(next_sym.id)
            if next_sym.id not in self.device_dict:
                raise UndefinedError(next_sym, device_name)

            device_type = self.device_dict[next_sym.id]['type']
            if device_type != self.scanner.CLOCK_id:
                raise InvalidClockName(next_sym, device_name)

            device_symbols.append(next_sym)

            next_sym = self.scanner.get_symbol()
            # next one is either a connection work or a comma
            if next_sym.id in connect:
                checking_devices = False
                next_sym = self.scanner.get_symbol()
                # ignore 'length' if it appears
                if next_sym.id == self.scanner.length_id:
                    next_sym = self.scanner.get_symbol()

                # next symbol needs to be a number
                if next_sym.type == self.scanner.NUMBER:
                    # check if it is a number in the correct range
                    clock_length = next_sym.id
                    if clock_length <= 1000:
                        # add this to device property
                        for sym in device_symbols:
                            self.device_dict[sym.id]['property'] = clock_length
                    else:
                        InvalidClockLength(next_sym)
                else:
                    raise InvalidClockLength(next_sym)

                next_sym = self.scanner.get_symbol()
                if next_sym.type != self.scanner.SEMICOLON:
                    raise SemicolonError(next_sym)

            elif next_sym.type == self.scanner.COMMA:
                next_sym = self.scanner.get_symbol()

            else:
                checking_devices = False
                raise InvalidInitClockRule(next_sym)

        return next_sym

    def init_gate(self, symbol):
        next_sym = symbol
        connect = [self.scanner.has_id, self.scanner.have_id]
        device_types = [self.scanner.AND_id,
                        self.scanner.OR_id,
                        self.scanner.NOR_id,
                        self.scanner.XOR_id,
                        self.scanner.NOT_id,
                        self.scanner.NAND_id]
        checking_devices = True
        device_symbols = []

        has_XOR = False
        has_NOT = False

        while checking_devices:
            symbol = next_sym

            if next_sym.type != self.scanner.NAME:
                raise InvalidDeviceName(next_sym)

            device_name = self.names.get_name_string(next_sym.id)
            if next_sym.id not in self.device_dict:
                raise UndefinedError(next_sym, device_name)

            device_type = self.device_dict[next_sym.id]['type']

            if device_type == self.scanner.DTYPE_id:
                raise AttemptToDefineDTYPEInputs(next_sym)

            elif device_type == self.scanner.XOR_id:
                has_XOR = True
            elif device_type == self.scanner.NOT_id:
                has_NOT = True

            device_symbols.append(next_sym)

            next_sym = self.scanner.get_symbol()
            # next one is either a connection word or a comma
            if next_sym.id in connect:

                checking_devices = False
                next_sym = self.scanner.get_symbol()
                # define number of inputs
                # next symbol has to be a number between 1-16 unless NOT or XOR
                # NOT has one input only
                # XOR has two inputs

                if next_sym.type == self.scanner.NUMBER:
                    # if XOR, inputs need to be exactly 2

                    if has_XOR:
                        if next_sym.id != 2:
                            raise InvalidXORInputNumber(
                                next_sym)  # XOR inputs error
                    # if NOT, inputs need to be exactly 1
                    elif has_NOT:
                        if next_sym.id != 1:
                            raise InvalidNOTInputNumber# NOT inputs error
                    else:
                        if next_sym.id > 16:
                            raise InvalidInputNumber(next_sym)

                    input_number = next_sym.id
                    # check if the next symbol says 'inputs'
                    next_sym = self.scanner.get_symbol()
                    inputs = [self.scanner.inputs_id, self.scanner.input_id]
                    if next_sym.id in inputs:
                        # add this to the device for connecting up later
                        for sym in device_symbols:
                            self.device_dict[sym.id]['property'] = input_number
                    else:
                        raise InputsDefinedIncorrectly(next_sym)

                else:
                    # expected an input number
                    raise InputNumberMissing(next_sym)

                next_sym = self.scanner.get_symbol()
                if next_sym.type != self.scanner.SEMICOLON:
                    raise SemicolonError(next_sym)

            elif next_sym.type == self.scanner.COMMA:
                next_sym = self.scanner.get_symbol()

            else:
                checking_devices = False
                raise InvalidInitDeviceRule(next_sym)

        return next_sym

# ===========================================================================================================
# ===========================================================================================================

    def connections_block(self, symbol):
        """Check if symbols form a connections block.

        """
        next_sym = self.scanner.get_symbol()

        if next_sym.type == self.scanner.OPEN_BRACKET:
            self.in_block = True
            next_sym = self.scanner.get_symbol()
            while next_sym.type != self.scanner.CLOSE_BRACKET:
                if next_sym.type == self.scanner.EOF:
                    # raise a close bracket error
                    raise CloseBracketError(next_sym)
                next_sym = self.connections_subrule(next_sym)
            self.in_block = False
            next_sym = self.scanner.get_symbol()
        else:
            raise OpenBracketError(next_sym)  # raise open bracket error
        return next_sym

    def connections_subrule(self, symbol):
        self.input_symbols = []
        try:
            next_sym = self.parse_output_rule(symbol)

            # check for 'to' or 'is connected to'
            if next_sym.id == self.scanner.to_id:
                pass
            elif next_sym.id == self.scanner.is_id:
                # next two words need to form 'is connected to'
                next_sym = self.scanner.get_symbol()
                if next_sym.id != self.scanner.connected_id:
                    raise ConnectedToError(next_sym)

                next_sym = self.scanner.get_symbol()
                if next_sym.id != self.scanner.to_id:
                    raise ConnectedToError(next_sym)

            else:
                # expected 'to' or 'is connected to'
                raise ConnectedToError(next_sym)

            next_sym = self.scanner.get_symbol()
            next_sym = self.parse_input_rule(next_sym)

            while next_sym.type == self.scanner.COMMA:
                next_sym = self.scanner.get_symbol()
                next_sym = self.parse_input_rule(next_sym)

            # make the output-input connections!
            self.make_connections()

            if next_sym.type != self.scanner.SEMICOLON:
                raise SemicolonError(next_sym)

            next_sym = self.scanner.get_symbol()

        except ParserError as e:
            self.add_error(e)
            next_sym = self.skip_error(e)

        return next_sym

    def parse_output_rule(self, symbol):
        """Check if the scanner symbols form an output."""
        # name, [".", output_name]
        if symbol.type == self.scanner.NAME:
            name_symbol = symbol
        else:
            raise InvalidDeviceName(symbol)

        next_sym = self.scanner.get_symbol()
        if next_sym.type == self.scanner.DOT:
            # has output port
            pass
        else:
            # no output port
            # check if its a dtype and raise an error
            device_type = self.device_dict[name_symbol.id]['type']
            if device_type == self.scanner.DTYPE_id:
                raise NoDTYPEOutputPortError(next_sym)

            self.output_symbol = (name_symbol, None)
            return next_sym
        next_sym = self.scanner.get_symbol()
        if self.is_output_port(name_symbol, next_sym):
            output_port_symbol = next_sym
        else:
            raise OutputPortError(next_sym)

        next_sym = self.scanner.get_symbol()
        self.output_symbol = (name_symbol, output_port_symbol)
        return next_sym

    def parse_input_rule(self, symbol):
        """Check if the scanner symbols form an input."""
        # name, ".", input_name

        if symbol.type == self.scanner.NAME:
            name_symbol = symbol
        else:
            raise InvalidDeviceName(symbol)

        next_sym = self.scanner.get_symbol()
        if next_sym.type == self.scanner.DOT:
            # has output port
            pass
        else:
            raise DotError(next_sym)

        next_sym = self.scanner.get_symbol()
        if self.is_input_port(name_symbol, next_sym):
            input_port_symbol = next_sym
        else:
            raise InputPortError(next_sym)

        next_sym = self.scanner.get_symbol()
        self.input_symbols.append((name_symbol, input_port_symbol))
        return next_sym

    def is_output_port(self, name_symbol, port_symbol):
        # output ports are only specified for d types
        # they can be either Q or QBAR
        device_type = self.device_dict[name_symbol.id]['type']
        if device_type == self.scanner.DTYPE_id:
            return port_symbol.id in [self.scanner.Q_id, self.scanner.QBAR_id]
        else:  # no other gates have different output ports
            return False

    def is_input_port(self, name_symbol, port_symbol):
        # input ports
        device_type = self.device_dict[name_symbol.id]['type']
        multi_input_gates = [self.scanner.AND_id,
                             self.scanner.OR_id,
                             self.scanner.NOR_id,
                             self.scanner.XOR_id,
                             self.scanner.NOT_id,
                             self.scanner.NAND_id]

        if device_type == self.scanner.DTYPE_id:
            possible_inputs = [
                self.scanner.CLK_id,
                self.scanner.SET_id,
                self.scanner.CLEAR_id,
                self.scanner.DATA_id,
            ]
            return port_symbol.id in possible_inputs

        elif device_type in multi_input_gates:
            num_inputs = self.device_dict[name_symbol.id]['property']
            # inputs have format I1, I2 ...
            port_name = self.names.get_name_string(port_symbol.id)
            if len(port_name) < 2:
                return False
            else:
                if port_name[0] != 'I':
                    return False
                if port_name[1:].isnumeric():
                    if int(port_name[1:]) <= num_inputs:
                        return True
                return False
        else:
            return False

# =============================================================================
# =============================================================================

    def monitors_block(self, symbol):
        """Check if symbols form a monitors block.

        """
        next_sym = self.scanner.get_symbol()

        if next_sym.type == self.scanner.OPEN_BRACKET:
            self.in_block = True
            next_sym = self.scanner.get_symbol()
            while next_sym.type != self.scanner.CLOSE_BRACKET:
                if next_sym.type == self.scanner.EOF:
                    # raise a close bracket error
                    raise CloseBracketError(next_sym)
                next_sym = self.monitors_subrule(next_sym)
            self.in_block = False
            next_sym = self.scanner.get_symbol()
        else:
            raise OpenBracketError(next_sym)  # raise open bracket error
        return next_sym

    def monitors_subrule(self, symbol):
        # we can only monitor outputs
        try:
            next_sym = self.parse_output_rule(symbol)
            self.make_monitor()

            while next_sym.type == self.scanner.COMMA:
                next_sym = self.scanner.get_symbol()
                next_sym = self.parse_output_rule(next_sym)
                self.make_monitor()

            if next_sym.type != self.scanner.SEMICOLON:
                raise SemicolonError(next_sym)

            next_sym = self.scanner.get_symbol()

        except ParserError as e:
            # add the error
            self.add_error(e)
            # skip to the next error
            next_sym = self.skip_error(e)
        return next_sym

# =============================================================================
# =============================================================================

    def make_devices(self):
        for device_id, device_details in self.device_dict.items():
            type = device_details['type']
            property = device_details['property']
            # need to check for errors here
            self.devices.make_device(device_id, type, property)

    def make_connections(self):
        for input, input_port_symbol in self.input_symbols:
            output_id = self.output_symbol[0].id
            output_port = self.output_symbol[1]
            output_port_id = None
            if output_port:
                output_port_id = output_port.id

            input_id = input.id
            input_port_id = None
            if input_port_symbol:
                input_port_id = input_port_symbol.id
            self.network.make_connection(
                input_id, input_port_id, output_id, output_port_id)

    def make_monitor(self):
        output = self.output_symbol[0]
        output_id = output.id

        output_port = self.output_symbol[1]
        output_port_id = None
        if output_port:
            output_port_id = output_port.id

        self.monitors.make_monitor(output_id, output_port_id)

# =============================================================================
# =============================================================================

    def check_all_inputs_connected(self):
        # check that everything that is an input has been
        # connected to something
        # specify exactly which input has not been connected
        for device in self.devices.devices_list:
            for input_id, connection in device.inputs.items():
                if connection is None:
                    self.input_not_connected_errors.append(
                        (
                            self.names.get_name_string(device.device_id),
                            self.names.get_name_string(input_id)
                        )
                    )

    def add_error(self, error):
        if isinstance(error, ParserSyntaxError):
            self.syntax_errors.append(error)
        elif isinstance(error, ParserSemanticError):
            self.semantic_errors.append(error)
        else:
            raise error

    def skip_error(self, error):  # skip to end of current statement/block
        next_sym = error.symbol
        if self.in_block:  # skip until next semicolon or closed bracket
            end_types = [self.scanner.SEMICOLON,
                         self.scanner.CLOSE_BRACKET, self.scanner.EOF]

            while next_sym.type not in end_types:  # skip until the next
                next_sym = self.scanner.get_symbol()
            # returns close bracket to exit the block
            if next_sym.type == self.scanner.CLOSE_BRACKET:
                return next_sym

        else:
            next_sym = error.symbol
            end_types = [self.scanner.CLOSE_BRACKET, self.scanner.EOF]
            while next_sym.type not in end_types:
                next_sym = self.scanner.get_symbol()

        next_sym = self.scanner.get_symbol()
        return next_sym

    def print_errors(self):
        """Print all the errors that have been caught."""
        if len(self.syntax_errors) > 0:
            for error in self.syntax_errors:
                symbol = error.symbol
                self.scanner.print_error_line(symbol.line_number,
                                              symbol.line_position,
                                              error.message)

        if len(self.semantic_errors) > 0:
            for error in self.semantic_errors:
                symbol = error.symbol
                self.scanner.print_error_line(symbol.line_number,
                                              symbol.line_position,
                                              error.message)

        if len(self.input_not_connected_errors) > 0:
            for device_name, input_name in self.input_not_connected_errors:
                print("'{}.{}' is not connected"
                      .format(device_name, input_name))
            print("{} unconnected inputs found.".format(
                len(self.input_not_connected_errors)
            ))

# =============================================================================
# =============================================================================

    def parse_network(self):
        """Parse the circuit definition file."""
        symbol = self.scanner.get_symbol()

        # blocks need to be discovered in the right order and not repeated
        header_order = [self.scanner.devices_id, self.scanner.initialise_id,
                        self.scanner.connections_id, self.scanner.monitors_id]
        header_functions = [self.devices_block, self.initialise_block,
                            self.connections_block, self.monitors_block]

        header_index = 0

        # keep checking symbols until the end of the file
        while symbol.type != self.scanner.EOF:
            try:
                if symbol.type == self.scanner.KEYWORD:

                    if symbol.id == header_order[header_index]:
                        next_sym = header_functions[header_index](symbol)
                        header_index += 1
                    else:

                        raise InvalidBlockHeaderOrder(
                            symbol)  # expected a block header

                else:
                    raise InvalidBlockHeader(symbol)  # expected a keyword
            except ParserError as e:
                # add the error
                self.add_error(e)
                # skip to the next error
                next_sym = self.skip_error(e)
            symbol = next_sym

        self.check_all_inputs_connected()
        self.print_errors()

        self.scanner.file.close()

        return len(self.syntax_errors) == 0 and \
            len(self.semantic_errors) == 0 and \
            len(self.input_not_connected_errors) == 0
