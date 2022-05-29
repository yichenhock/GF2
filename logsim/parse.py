"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""

from errno import ENOTCONN
from re import S
from names import Names
from scanner import Symbol, Scanner
from devices import Device, Devices
from network import Network
from monitors import Monitors
from error import SemanticError, SyntaxError

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
        self.syntax = SyntaxError()
        self.semantic = SemanticError()

        self.block = []
        self.user_object_dictionary = []
        self.user_object_type = []
        
        # T_T
        self.block_ids = [self.scanner.devices_id, self.scanner.initialise_id, self.scanner.connections_id, self.scanner.monitors_id]

        self.possession_ids = [self.scanner.has_id, self.scanner.have_id]

        self.definition_ids = [self.scanner.is_id, self.scanner.are_id]

        self.other_keywords_ids = [self.scanner.to_id, self.scanner.connected_id, self.scanner.input_id, self.scanner.inputs_id, self.scanner.cycle_id, self.scanner.length_id, self.scanner.clk_id, self.scanner.sw_id, self.scanner.I_id]

        self.gate_type_ids = [self.scanner.AND_id, self.scanner.OR_id, self.scanner.NOR_id, self.scanner.XOR_id, self.scanner.NAND_id, self.scanner.DTYPE_id]

        self.switch_id = [self.scanner.SWITCH_id]

        self.clock_id = [self.scanner.CLOCK_id]

        self.switch_level = [self.scanner.HIGH_id, self.scanner.LOW_id]

        self.dtype_inputs = [self.scanner.DATA_id, self.scanner.CLK_id, self.scanner.CLEAR_id, self.scanner.SET_id]

        self.dtype_outputs = [self.scanner.Q_id, self.scanner.QBAR_id]
    	
    def circuit_description(self):
        """Check the header for each block exists, and is not misspelled. 

        Call relevant block function.
        
        """

        # Read the first thing of each block
        self.symbol = self.scanner.get_symbol()

        # Check if first keyword is a devices
        if (self.symbol.type == self.scanner.KEYWORD 
        	and self.symbol.id == self.scanner.devices_id):
            self.block.append("devices")
            self.devices_block()

        # Check if next keyword is initialise
        if (self.symbol.type == self.scanner.KEYWORD 
        	and self.symbol.id == self.scanner.initialise_id):
            self.devices_block()
        
        # Check if next keyword is connections
        if (self.symbol.type == self.scanner.KEYWORD 
        	and self.symbol.id == self.scanner.connections_id):
            self.devices_block()
        
        # Check if next keyword is monitors
        if (self.symbol.type == self.scanner.KEYWORD 
        	and self.symbol.id == self.scanner.monitors_id):
            self.devices_block()

        # If the symbol we expect is any header but we get a bracket, then we can report the header as missing
        elif self.symbol.type == self.scanner.OPEN_BRACKET:
            self.syntax.print(self.syntaxerror.NO_HEADER)
            self.skip_block()

        # Incorrect header
        else:
            self.syntax.print(self.syntaxerror.HEADER_NAME_ERROR)
            self.skip_block() 

    def skip_block(self):
        """Skip entire block because it is not possible to know what is supposed to be inside, by repeatedly calling skip_line() from the Scanner class.

        For header name errors.
        """

        while (self.symbol.id not in self.block_ids and self.symbol.type != self.scanner.EOF):
            self.scanner.skip_line()
        if len(self.block) <= 4:
            self.circuit_description()

    def devices_block(self):
        """Operate at level of parsing a device block."""

        # Fetch next symbol after section heading and check it's a bracket
        self.symbol = self.scanner.get_symbol()

        if self.symbol != self.scanner.BRACKET_OPEN:
            # If not a bracket, skip to next character (unique handling method to this error)
            self.scanner.print_error_line("NO_OPEN_BRACKET", "Missing open parentheses following section or subsection header.")
            self.scanner.advance

             # Skip device block, end reached
            if self.symbol == self.scanner.BRACKET_CLOSE:
                return
            # If we haven't reached the end of the device block yet, call device_definition() to define another device
            # This works even if we have no device definition inside the block and the bracket is missing
            # device_definition() will register a missing device name in this case
            else:
                self.device_definition()

        # If bracket exists:
        else:
            # Call line-level function as long as end of block not reached
            while self.symbol.type != self.scanner.BRACKET_CLOSE:
                self.device_definition()
                # Read first symbol of next line
                self.symbol = self.scanner.get_symbol()

            # Exit while loop when symbol stored is a closed bracket
            # End of functionality of devices_block function
            return 

    def initialise_block(self):
        return None

    def connections_block(self):
        return None
    
    def monitors_block(self):
        return None

    def device_definition(self):
        """Parse gate and check gate.

        Used inside devices block for defining the device names and their corresponding types.
        
        It should be read at the point after the parser gets the first symbol of each line, and finish without having read the first symbol of the next line.
        """

        self.device_name()

            while self.symbol.type == self.scanner.COMMA:
                current_name = self.names.names[self.symbol.id]
                self.symbol = self.scanner.get_symbol()

            if self.symbol.type == self.scanner.KEYWORD and self.symbol.id in self.definition_ids:
                self.symbol = self.scanner.get_symbol()
                if self.symbol.id not in self.gate_type_ids:
                    if self.symbol.id in self.switch_id or self.clock_id:
                        # Semantic error - device type
                        pass
                    else:
                        printerror = SyntaxError(SyntaxError.DEVICE_TYPE_ERROR)
                else:
                    # Do something to call the device class
                    pass

        # No device name found at the beginning of the line inside the device class but not reached end of block yet
        elif self.symbol.id != self.scanner.BRACKET_CLOSE:
            self.syntax.print(self.syntax.DEVICE_NAME_MISSING)

        elif self.symbol.id == self.scanner.BRACKET_CLOSE:
            return
    
    def switch_definition(self):
        """Parse switch and check switch

        Used inside devices for initialisation.
        
        """
        return None
    
    def clock_definition(self):
        return None
    
    def gate_initialisation(self):
        return None
    
    def switch_initialisation(self):
        return None
    
    def clock_initialisation(self):
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
        # If first symbol is of type NAME (for all gates and DTYPE)
        if self.symbol.type == self.scanner.NAME:
            current_name = self.names.names[self.symbol.id]

            self.is_legal_name = True

            # Check if all letters in device name are lowercase
            for i in current_name:
                if i.isalpha():
                    if i.isupper():
                        self.syntax.print(self.syntax.DEVICE_LETTER_CAPITAL)
                        self.is_legal_name = False

            # If name is legal, append to name list
            if self.is_legal_name:
                self.user_object_list.append(current_name)
    
    def clock_name(self):
        return None
    
    def switch_name(self):
        return None
    
    def parse_network(self):
        """Parse the circuit definition file."""
        # Main idea: should check overall blocks and append order to self.block. Do a check for self.block at the end to see if the main structure follows

        # Tree structure: split into blocks
        while len(self.block) <= 4:
            self.circuit_description()
        return True

