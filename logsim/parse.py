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

        # self.syntax_error_count = 0
        # self.semantic_error_count = 0

        self.syntax_errors = []
        self.semantic_errors = []
        self.input_not_connected_errors = []
        self.name_symbols = []
        self.input_symbols = []
        self.output_symbol = None 
        self.monitor_symbols = []
        self.device_input_num = {} # {device_id: number_inputs}
        # num inputs only for AND, NAND, OR, NOR

        self.definition_statements = [self.scanner.is_id, self.scanner.are_id]
        self.possession_statements = [self.scanner.has_id, self.scanner.have_id]

    def devices_block(self): 
        """Check if symbols form a device block.
        
        """
        print('devices block')
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
        try: 
            print(symbol.id)
            # print(self.names.get_name_string(symbol.id))

            # substatement = [[], [], []] # [devices, connection, type]

            # if symbol.type == self.scanner.NAME: 
            #     # loop until it gets to 'IS' or 'ARE'
            #     next_sym = self.scanner.get_symbol()

            #     device_ids = []
            #     while next_sym.type != self.scanner.is_id: 
            #         if next_sym.type == self.scanner.EOF:
            #             raise ParserError # raise expected a 'IS' or 'ARE'
                    
            #         # if next_sym.type
            #         next_sym = self.scanner.get_symbol()

            # else: 
            #     raise ParserError # expected a name


            # if next_sym.type == self.scanner.SEMICOLON: 
            #     pass
            # else: 
            #     raise ParserError # expected a semicolon

            next_sym = self.scanner.get_symbol()

        except ParserError as e: 
            self.add_error(e)
            next_sym = self.skip_error(e)

        return next_sym

    def initialise_block(self, symbol):
        print('initialise block')
        return self.scanner.getsymbol()

    def connections_block(self, symbol): 
        print('connections block')
        return self.scanner.getsymbol()
    
    def monitors_block(self, symbol): 
        print('monitors block')
        return self.scanner.getsymbol()

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
            
            end_ids = [self.scanner.SEMICOLON, self.scanner.CLOSE_BRACKET, self.scanner.EOF]
            while next_sym.type not in end_ids: # skip until the next 
                next_sym = self.scanner.get_symbol() 

            if next_sym.type == self.scanner.ClOSE_BRACKET: # returns close bracket to exit the block
                return next_sym

        else: 
            next_sym = error.symbol
            end_ids = [self.scanner.CLOSE_BRACKET, self.scanner.EOF]
            while next_sym not in end_ids:
                next_symbol = self.scanner.get_symbol()

        next_sym = self.scanner.get_symbol()
        return next_sym

    def print_errors(self):
        """Print all the errors that have been caught."""
        if len(self.syntax_errors) > 0: 
            for error in self.syntax_errors:
                symbol = error.symbol
                message = error.message
                # self.scanner.print_error_line()
                print(symbol, message)

        if len(self.semantic_errors) > 0:
            for error in self.semantic_errors:
                symbol = error.symbol
                message = error.message
                # self.scanner.print_error_line()
                print(symbol, message)

        if len(self.input_not_connected_errors) > 0:
            for error in self.input_not_connected_errors:
                symbol = error.symbol
                message = error.message
                # self.scanner.print_error_line()
                print(symbol, message)

#===========================================================================================================
#===========================================================================================================

    def parse_network(self):
        """Parse the circuit definition file."""
        symbol = self.scanner.get_symbol()

        # keep checking symbols until the end of the file
        while symbol.type != self.scanner.EOF: 
            print(symbol.id)
            try: 
                if symbol.type == self.scanner.KEYWORD: 
                    if symbol.id == self.scanner.devices_id: 
                        next_sym = self.devices_block()
                    elif symbol.id == self.scanner.initialise_id:
                        next_sym = self.initialise_block()
                    elif symbol.id == self.scanner.connections_id:
                        next_sym = self.connections_block()
                    elif symbol.id == self.scanner.monitors_id: 
                        next_sym = self.monitors_block()
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
