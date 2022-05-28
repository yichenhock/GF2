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
from error_backup import OpenParentheses, CloseParentheses, BlockHeader, DeviceName, IllegalDeviceName,

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
        """Check that the file main structure follows the form defined in the EBNF."""
        if (self.symbol.type == self.scanner.KEYWORD 
        	and self.symbol.id == self.scanner.devices_id):
            self.devices_block()
        else:
            # Missing device blocl
        self.symbol = self.scanner.get_symbol()
        if (self.symbol.type == self.scanner.KEYWORD 
        	and self.symbol.id == self.scanner.initialise_id):
            self.devices_block()

    # def skip_block(self):
    #     self.symbol = self.scanner.get_symbol()
    #     if self.symbol.type == self.scanner.BRACKET_OPEN:
    #             while self.symbol.type != self.scanner.BRACKET_CLOSE:
    #                 self.scanner.skip_line()
    #                 # Read symbol at start of each line only to check for bracket close
    #                 self.symbol = self.scanner.get_symbol()
    #             # Skip the semicolon at the end of the section 
    #             self.symbol = self.scanner.get_symbol()
    
    def devices_block(self):
        self.symbol = self.scanner.get_symbol()
        if (self.symbol.type == self.scanner.KEYWORD 
            and self.symbol.id == self.scanner.devices_id):
            self.symbol = self.scanner.get_symbol()
            if self.symbol != self.scanner.BRACKET_OPEN:
                # Raise bracket open error
            self.symbol = self.scanner.get_symbol()
            self.object_initialisation(self.line)
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self.object_initialisation(device_type)
            
        else:
            # Missing device ID
            pass
        return
    
    def initialise_block(self):
        return None

    def connections_block(self):
        return None
    
    def monitors_block(self):
        return None
    
    def object_initialisation(self, line):
        """Calls on device_definition(), c() and switch()"""
        
        if self.symbol.type == self.scanner.NAME:
            device_definition()

        elif self.symbol.type == self.scanner.KEYWORD:
            if self.symbol.id == self.scanner.sw_id:
                switch_definition()

            elif self.symbol.id == self.scanner.clk_id:
                clock_definition()
        
        else:

            # Missing name

    def device_definition(self):
        """Parse gate and check gate.

        Used inside devices for initialisation.
        
        """
        current_name = self.names.names[self.symbol.id]
        if current_name[0].islower():
            # Name does not with lowercase letter
        else:
            self.user_object_list.append(current_name)
        while self.symbol.type == self.scanner.COMMA:
            device_add_name()
            self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id in self.definition_ids:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.id not in self.gate_type_ids:
                if self.symbol.id in self.switch_id or self.clock_id:
                    # Semantic error
                else:
                    # Syntax error
            else:
                # Do something to call the device class
        return None
    
    def device_add_name(self):
        if not self.names.names[self.symbol.id][0].islower():
            # Name does not with lowercase letter
        # current_name = ""
        # current_name += self.names.names[self.symbol.id]
        # while self.symbol.type != self.scanner.COMMA or self.symbol.id not in self.posession_ids:
        #     current_name += self.names.names[self.symbol.id]
        self.user_object_list.append(current_name)
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

