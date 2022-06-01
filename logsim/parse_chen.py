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

from error_chen import ParserError

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

        self.syntax_error_count = 0
        self.semantic_error_count = 0

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
        """Check if symbols form a device block
        
        """
        next_sym = self.scanner.get_symbol()

        if next_sym.type == self.scanner.OPEN_BRACKET:
            self.in_block = True 
            next_sym = self.scanner.get_symbol()

            while next_sym.type != self.scanner.CLOSE_BRACKET: 
                if next_sym.type == self.scanner.EOF: 
                    raise ParserError # raise a close bracket error
                next_sym = self.devices_subrule(next_sym)
            self.in_block = False 
            next_sym = self.scanner.get_symbol()
        else: 
            raise ParserError # raise open bracket error
        return next_sym

    def devices_subrule(self, symbol: Symbol) -> Symbol:
        try: 
            substatement = [[], [], []] # [devices, connection, type]

            if symbol.type == self.scanner.NAME: 
                # loop until it gets to 'IS' or 'ARE'
                next_sym = self.scanner.get_symbol()

                device_ids = []
                while next_sym.type != self.scanner.is_id: 
                    if next_sym.type == self.scanner.EOF:
                        raise ParserError # raise expected a 'IS' or 'ARE'
                    
                    
                    # if next_sym.type
                    
                    next_sym = self.scanner.get_symbol()

            else: 
                raise ParserError # expected a name


            if next_sym.type == self.scanner.SEMICOLON: 
                pass
            else: 
                raise ParserError # expected a semicolon

            next_sym = self.scanner.get_symbol()

        except ParserError as e: 
            self.add_error(e)
            next_symbol = self.skip_error(e)

        return next_symbol

    def initialise_block(self):
        return 

    def connections_block(self): 
        return 
    
    def monitors_block(self): 
        return 

#===========================================================================================================
#===========================================================================================================

    def check_all_inputs_connected(self):
        return 

    def add_error(self, error):
        pass
  
    def skip_error(self, error): # skip to end of current statement/block
        if self.in_block: # skip until next semicolon or closed bracket
            pass
        else: # skip until the next 
            pass

        next_sym = self.scanner.get_symbol()
        return next_sym

    def print_errors(self):
        pass

#===========================================================================================================
#===========================================================================================================

    def parse_network(self):
        """Parse the circuit definition file."""
        symbol = self.scanner.get_symbol()

        while symbol.type != self.scanner.EOF: 
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
                        raise ParserError # expected a block header
                else:
                    raise ParserError # expected a keyword
            except ParserError as e: 
                # add the error 
                self.add_error(e)
                # skip to the next error 
                next_sym = self.skip_error(e)
            symbol = next_sym
        
        self.check_all_inputs_connected()
        self.print_errors()

        return True # only if there are no errors
