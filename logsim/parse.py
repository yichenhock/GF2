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
    InvalidInputNumber
)

# Syntax errors
from error import (
    BlockError,
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
    InputsDefinedIncorrectly
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

        self.in_block = False # True if parser inside a block

        self.syntax_errors = []
        self.semantic_errors = []
        self.input_not_connected_errors = []

        self.names_parsed = []

        self.input_symbols = []
        self.output_symbol = None 
        self.monitor_symbols = []

        self.device_dict = {} # {device_id: device_kind, device_property=None}

        # self.device_input_num = {} # {device_id: number_inputs}
        # num inputs only for AND, NAND, OR, NOR

    def devices_block(self, symbol): 
        """Check if symbols form a device block.
        
        """
        print('devices_block')
        next_sym = self.scanner.get_symbol()

        if next_sym.type == self.scanner.OPEN_BRACKET:
            self.in_block = True 
            next_sym = self.scanner.get_symbol()
            while next_sym.type != self.scanner.CLOSE_BRACKET: 
                if next_sym.type == self.scanner.EOF: 
                    raise CloseBracketError(next_sym) # raise a close bracket error
                next_sym = self.devices_subrule(next_sym)
            self.in_block = False 
            next_sym = self.scanner.get_symbol()
        else: 
            raise OpenBracketError(next_sym) # raise open bracket error
        return next_sym

    def devices_subrule(self, symbol):
        print('devices_subrule')
        try: 
            connect = [self.scanner.is_id, self.scanner.are_id]
            types = [self.scanner.AND_id,
                    self.scanner.OR_id, 
                    self.scanner.NOR_id, 
                    self.scanner.XOR_id, 
                    self.scanner.NAND_id, 
                    self.scanner.DTYPE_id,
                    self.scanner.SWITCH_id, 
                    self.scanner.CLOCK_id]
            name_symbols = []
            checking_devices = True 

            while checking_devices:
                if symbol.type == self.scanner.NAME:

                    if self.names.get_name_string(symbol.id) in self.names_parsed:
                        raise RedefinedError(symbol, self.names.get_name_string(symbol.id))
                    else: 
                        self.names_parsed.append(self.names.get_name_string(symbol.id))
                        name_symbols.append(symbol)

                    # now expect either 'IS/ARE' or 'COMMA, NAME'
                    symbol = self.scanner.get_symbol()

                    if symbol.id in connect: # go to detect the device!
                        checking_devices = False
                        symbol = self.scanner.get_symbol()
                        if symbol.id in types:
                            # first check if the names are legal
                            for name_symbol in name_symbols: 
                                self.check_name_legal(name_symbol, symbol.id)
                                # add to devices for connecting up later
                                # devices can only be connected after initialise block
                                self.device_dict[name_symbol.id] = {
                                    'type': symbol.id,
                                    'property': None
                                    }
                        else:
                            raise DeviceTypeError(symbol) # expected a device type
                        
                        symbol = self.scanner.get_symbol()
                        if symbol.type != self.scanner.SEMICOLON:
                            raise SemicolonError(symbol)

                    elif symbol.type == self.scanner.COMMA: 
                        symbol = self.scanner.get_symbol()

                    else:
                        checking_devices = False
                        raise InvalidDeviceRule(symbol) # invalid device subrule statement
                else:
                    checking_devices = False
                    raise InvalidDeviceName(symbol) # expected a valid device name 

            next_sym = self.scanner.get_symbol()

        except ParserError as e: 
            self.add_error(e)
            next_sym = self.skip_error(e)

        return next_sym

    def check_name_legal(self, name_symbol, component_type):
        name = self.names.get_name_string(name_symbol.id)
        if not name.islower(): # device names have to be all lower case
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
            if self.is_switch_legal(name) == True or self.is_clock_legal(name) == True:
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
        # returns true if name starts with 'clk' followed by a number or nothing
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

#===========================================================================================================
#===========================================================================================================

    def initialise_block(self, symbol):
        """Check if symbols form a initialise block.
        
        """

        next_sym = self.scanner.get_symbol()

        if next_sym.type == self.scanner.OPEN_BRACKET:
            self.in_block = True 
            next_sym = self.scanner.get_symbol()
            while next_sym.type != self.scanner.CLOSE_BRACKET: 
                if next_sym.type == self.scanner.EOF: 
                    raise CloseBracketError(next_sym) # raise a close bracket error
                next_sym = self.initialise_subrule(next_sym)
            self.in_block = False 
            next_sym = self.scanner.get_symbol()
        else: 
            raise OpenBracketError(next_sym) # raise open bracket error
        return next_sym

    def initialise_subrule(self, symbol):
        print('initialise_subrule')
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
                    raise UndefinedError(symbol, self.names.get_name_string(symbol.id))
            else: 
                raise InvalidDeviceName(symbol)

            next_sym = self.scanner.get_symbol()

        except ParserError as e:
            self.add_error(e)
            next_sym = self.skip_error(e)

        return next_sym

    def init_switch(self, symbol):
        print('init switch')
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
        print('init clock')
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
        print('init gate')
        next_sym = symbol
        connect = [self.scanner.has_id, self.scanner.have_id]
        device_types = [self.scanner.AND_id,
                self.scanner.OR_id, 
                self.scanner.NOR_id, 
                self.scanner.XOR_id, 
                self.scanner.NAND_id, 
                self.scanner.DTYPE_id]
        checking_devices = True
        device_symbols = []
        while checking_devices:
            if next_sym.type != self.scanner.NAME:
                raise InvalidDeviceName(next_sym)
                
            device_name = self.names.get_name_string(next_sym.id)
            if next_sym.id not in self.device_dict:
                raise UndefinedError(next_sym, device_name)

            device_type = self.device_dict[next_sym.id]['type']
            if device_type not in device_types:
                raise InvalidDeviceName(next_sym, device_name)
            
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
                    raise InputNumberMissing(next_sym) # expected an input number

                next_sym = self.scanner.get_symbol()
                if next_sym.type != self.scanner.SEMICOLON:
                    raise SemicolonError(next_sym)

            elif next_sym.type == self.scanner.COMMA:
                next_sym = self.scanner.get_symbol()

            else:
                checking_devices = False
                raise InvalidInitDeviceRule(next_sym)

        return next_sym

#===========================================================================================================
#===========================================================================================================

    def connections_block(self, symbol): 
        print('connections block')

        return self.scanner.get_symbol()
    
#===========================================================================================================
#===========================================================================================================

    def monitors_block(self, symbol): 
        print('monitors block')

        return self.scanner.get_symbol()

#===========================================================================================================
#===========================================================================================================

    def make_devices(self):
        for device_id, device_details in self.device_dict.items():
            type = device_details['type']
            property = device_details['property']
            # need to check for errors here
            self.devices.make_device(device_id, type, property)

#===========================================================================================================
#===========================================================================================================

    def check_all_inputs_connected(self):
        # check that everything that is an input has been connected to something
        return 

    def add_error(self, error):
        if isinstance(error, ParserSyntaxError):
            self.syntax_errors.append(error)
        elif isinstance(error, ParserSemanticError):
            self.semantic_errors.append(error)
        else:
            raise error
  
    def skip_error(self, error): # skip to end of current statement/block
        next_sym = error.symbol
        if self.in_block: # skip until next semicolon or closed bracket
            end_types = [self.scanner.SEMICOLON, self.scanner.CLOSE_BRACKET, self.scanner.EOF]
            
            while next_sym.type not in end_types: # skip until the next 
                next_sym = self.scanner.get_symbol() 
            if next_sym.type == self.scanner.CLOSE_BRACKET: # returns close bracket to exit the block
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
                message = error.message
                self.scanner.print_error_line(symbol.line_number, 
                    symbol.line_position, error.message)

        if len(self.semantic_errors) > 0:
            for error in self.semantic_errors:
                symbol = error.symbol
                message = error.message
                self.scanner.print_error_line(symbol.line_number, 
                    symbol.line_position, error.message)

        if len(self.input_not_connected_errors) > 0:
            for error in self.input_not_connected_errors:
                symbol = error.symbol
                message = error.message
                self.scanner.print_error_line(symbol.line_number, 
                    symbol.line_position, error.message)

#===========================================================================================================
#===========================================================================================================

    def parse_network(self):
        """Parse the circuit definition file."""
        # print('testing scanner: ', self.scanner.CLOSE_BRACKET)
        symbol = self.scanner.get_symbol()

        # keep checking symbols until the end of the file
        while symbol.type != self.scanner.EOF: 
            try: 
                if symbol.type == self.scanner.KEYWORD: 
                    if symbol.id == self.scanner.devices_id: 
                        next_sym = self.devices_block(symbol)
                    elif symbol.id == self.scanner.initialise_id:
                        next_sym = self.initialise_block(symbol)
                    # elif symbol.id == self.scanner.connections_id:
                    #     next_sym = self.connections_block(symbol)
                    # elif symbol.id == self.scanner.monitors_id: 
                    #     next_sym = self.monitors_block(symbol)
                    else: 
                        raise BlockError(symbol) # expected a block header
                else:
                    raise BlockError(symbol) # expected a keyword
            except ParserError as e: 
                # add the error 
                self.add_error(e)
                # skip to the next error 
                next_sym = self.skip_error(e)
            symbol = next_sym
        
        print(self.device_dict)
        self.make_devices()

        self.check_all_inputs_connected()
        self.print_errors()

        return len(self.syntax_errors) == 0 and \
            len(self.semantic_errors) == 0 and \
            len(self.input_not_connected_errors) == 0
