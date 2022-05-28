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
from error import OpenParentheses, CloseParentheses, BlockHeader, DeviceName, IllegalDeviceName,

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
        self.names = Names()
        self.devices = Devices()
        self.network = Network()
        self.scanner = Scanner()
        self.monitors = Monitors()

        self.block = []

        self.possession_words = self.scanner.keywords_list[4:6]
        self.definition_words = self.scanner.keywords_list[6:8]
        self.gate_type = self.scanner.keywords_list[16:21]
        self.switch_level = ["HIGH", "LOW", 1, 0]
        self.dtype_inputs = self.scanner.keywords_list[-6:-2]
        self.dtype_outputs = self.scanner.keywords_list[-2:-1]

        # Use Python built-in function islower() to check for letters
        # Use Python built-in function isdigit() to check for digits
    	
    # def entirety(self):
    #     """Check that the file main structure follows the form defined in the EBNF."""
    #     if (self.symbol.type == self.scanner.KEYWORD 
    #     	and self.symbol.id == self.scanner.devices_id):
    #         self.block.append('M')
    #         self.skip_block()
    #         self.symbol = self.scanner.get_symbol()
    #         if (self.symbol.type == self.scanner.KEYWORD
    #             and self.symbol.id == self.scanner.initialise_id):
    #             self.block.append('I')
    #             self.skip_block()
    #             self.symbol = self.scanner.get_symbol()
    #         else:
    #             self.error()
    #     else:
    #         self.error()

    def skip_block(self):
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.BRACKET_OPEN:
                while self.symbol.type != self.scanner.BRACKET_CLOSE:
                    self.scanner.skip_line()
                    # Read symbol at start of each line only to check for bracket close
                    self.symbol = self.scanner.get_symbol()
                # Skip the semicolon at the end of the section 
                self.symbol = self.scanner.get_symbol()
    
    def devices_block(self):
        self.symbol = self.scanner.get_symbol()
        if (self.symbol.type == self.scanner.KEYWORD 
            and self.symbol.id == self.scanner.devices_id):
            self.symbol = self.scanner.get_symbol()
            if self.symbol != self.scanner.BRACKET_OPEN:
                raise OpenParentheses
            self.symbol = self.scanner.get_symbol()
            self.line = self.scanner.get_line()
            self.object_initialisation(self.line)
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self.object_initialisation(device_type)
            
        else:
            raise BlockHeader(self.block[-1])
        return None
    
    def initialise_block(self):
        return None

    def connections_block(self):
        return None
    
    def monitors_block(self):
        return None
    
    def object_initialisation(self, line):
        """Calls on gate(), dtype() and switch()"""
        if self.symbol[0].isdigit():
            raise IllegalDeviceName
        if not self.symbol[0].isalnum():
            raise DeviceName
        if line[-1] in self.gate_type:
            self.gate()
        elif line[-1] == self.scanner.keywords_list(21):
            self.dtype()
        elif line[-1] == self.scanner.keywords_list(22):
            self.switch()
        elif line[-1] == self.scanner.keywords_list(23):
            self.clock()
        return None

    def gate(self):
        """Parse gate and check gate.

        Used inside devices for initialisation.
        
        """
        return None
    
    def dtype(self):
        """Parse dtype and check dtype

        Used inside devices for initialisation.
        
        """
        return None
    
    def switch(self):
        """Parse switch and check switch

        Used inside devices for initialisation.
        
        """
        return None
    
    def clock(self):
        return None
    
    def inputs(self):
        return None
    
    def switch_initialisation(self):
        return None
    
    def clock_period(self):
        return None
    
    def connection_definition(self):
        return None
    
    def gate_input_name(self):
        return None
    
    def dtype_input_name(self):
        return None
    
    def dtype_output_name(self):
        return None
    
    def device_name(self):
        return None
    
    def clock_name(self):
        return None
    
    def switch_name(self):
        return None
    
    def error(self):
        return None
    
    def display_error(self, error_type):
        return None

    def parse_network(self):
        """Parse the circuit definition file."""
        # Main idea: should check overall blocks and append order to self.block. Do a check for self.block at the end to see if the main structure follows
        self.symbol = self.scanner.get_symbol()
        # Tree structure: split into blocks
        if (self.symbol.type == self.scanner.KEYWORD 
            and self.symbol.id == self.scanner.devices_id):
            # Append to block lister
            self.block.append('devices')
            # Skip past open bracket
            self.symbol = self.scanner.get_symbol()
            self.devices_block()
        return True

