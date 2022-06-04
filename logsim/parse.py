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
)

# Syntax errors
from error import (
    BlockError,
    SemicolonError,
    OpenBracketError,
    CloseBracketError,
    InvalidDeviceRule,
    DeviceTypeError,
    InvalidDeviceName
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
        self.device_input_num = {} # {device_id: number_inputs}
        # num inputs only for AND, NAND, OR, NOR

        self.definition_statements = [self.scanner.is_id, self.scanner.are_id]
        self.possession_statements = [self.scanner.has_id, self.scanner.have_id]

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
                    print('hihi')
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

            next_sym = symbol
            checking_devices = True 

            while checking_devices:
                if next_sym.type == self.scanner.NAME:
                    
                    if self.names.get_name_string(next_sym.id) in self.names_parsed:
                        raise RedefinedError(next_sym, self.names.get_name_string(next_sym.id))
                    else: 
                        self.names_parsed.append(self.names.get_name_string(next_sym.id))
                        name_symbols.append(next_sym)


                    # now expect either 'IS/ARE' or 'COMMA, NAME'
                    next_sym = self.scanner.get_symbol()

                    if next_sym.id in connect: # go to detect the device!
                        checking_devices = False
                        next_sym = self.scanner.get_symbol()
                        if next_sym.id in types:
                            # connect the device
                            self.make_device(next_sym.id, name_symbols)
                        else:
                            raise DeviceTypeError(next_sym) # expected a device type
                        
                        next_sym = self.scanner.get_symbol()
                        if next_sym.type != self.scanner.SEMICOLON:
                            raise SemicolonError(next_sym)

                    elif next_sym.type == self.scanner.COMMA: 
                        print('comma')
                        next_sym = self.scanner.get_symbol()

                    else:
                        checking_devices = False
                        raise InvalidDeviceRule(next_sym) # invalid device subrule statement
                else:
                    checking_devices = False
                    raise InvalidDeviceName(symbol) # expected a valid device name 

            next_sym = self.scanner.get_symbol()

        except ParserError as e: 
            self.add_error(e)
            next_sym = self.skip_error(e)

        return next_sym

    def initialise_block(self, symbol):
        print('initialise block')
        return self.scanner.get_symbol()

    def connections_block(self, symbol): 
        print('connections block')
        return self.scanner.get_symbol()
    
    def monitors_block(self, symbol): 
        print('monitors block')
        return self.scanner.get_symbol()

#===========================================================================================================
#===========================================================================================================

    def make_device(self, device_type, name_symbols=[]):

        if device_type == self.scanner.AND_id:
            print('AND gate!')
            for n in name_symbols:
                print(self.names.get_name_string(n.id))
        elif device_type == self.scanner.OR_id:
            print('OR gate!')
        elif device_type == self.scanner.NOR_id:
            print('NOR gate!')
        elif device_type == self.scanner.XOR_id:
            print('XOR gate!')
        elif device_type == self.scanner.NAND_id:
            print('NAND gate!')
        elif device_type == self.scanner.DTYPE_id:
            print('DTYPE!')
        elif device_type == self.scanner.SWITCH_id:
            print('SWITCH!')
        elif device_type == self.scanner.CLOCK_id:
            print('CLOCK!')

#===========================================================================================================
#===========================================================================================================

    def check_all_inputs_connected(self):
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
            print('in block error')
            end_types = [self.scanner.SEMICOLON, self.scanner.CLOSE_BRACKET, self.scanner.EOF]
            while next_sym.type not in end_types: # skip until the next 
                next_sym = self.scanner.get_symbol() 
            print('uwu1')
            if next_sym.type == self.scanner.CLOSE_BRACKET: # returns close bracket to exit the block
                print('uwu2')
                return next_sym
            print('uwu3')

        else: 
            print('not inblock error')
            next_sym = error.symbol
            end_types = [self.scanner.CLOSE_BRACKET, self.scanner.EOF]
            while next_sym.type not in end_types:
                next_sym = self.scanner.get_symbol()
        next_sym = self.scanner.get_symbol()

        return self.scanner.get_symbol()

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
            # print('something_parser:',self.names.get_name_string(symbol.id))
            try: 
                if symbol.type == self.scanner.KEYWORD: 
                    if symbol.id == self.scanner.devices_id: 
                        next_sym = self.devices_block(symbol)
                    # elif symbol.id == self.scanner.initialise_id:
                    #     next_sym = self.initialise_block(symbol)
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

        self.check_all_inputs_connected()
        self.print_errors()

        return len(self.syntax_errors) == 0 and \
            len(self.semantic_errors) == 0 and \
            len(self.input_not_connected_errors) == 0
