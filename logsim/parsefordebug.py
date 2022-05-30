"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""

from errno import ENOTCONN
from pickletools import read_unicodestring1
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

        self.names = names
        self.devices = devices
        self.network = network
        self.scanner = scanner
        self.monitors = monitors
        self.syntax = SyntaxError()
        self.semantic = SemanticError()

        self.user_object_name_list = []
        self.user_object_type_list = []
        self.user_object_input_num_list = []
        
        # T_T
        self.block_ids = [self.scanner.devices_id, self.scanner.initialise_id, self.scanner.connections_id, self.scanner.monitors_id]

        self.possession_ids = [self.scanner.has_id, self.scanner.have_id]

        self.definition_ids = [self.scanner.is_id, self.scanner.are_id]

        self.other_keywords_ids = [self.scanner.to_id, self.scanner.connected_id, self.scanner.input_id, self.scanner.inputs_id, self.scanner.cycle_id, self.scanner.length_id]

        self.gate_type_ids = [self.scanner.AND_id, self.scanner.OR_id, self.scanner.NOR_id, self.scanner.XOR_id, self.scanner.NAND_id, self.scanner.DTYPE_id]

        self.switch_id = [self.scanner.SWITCH_id]

        self.clock_id = [self.scanner.CLOCK_id]

        self.switch_level = [self.scanner.HIGH_id, self.scanner.LOW_id]

        self.dtype_inputs = [self.scanner.DATA_id, self.scanner.CLK_id, self.scanner.CLEAR_id, self.scanner.SET_id]

        self.dtype_outputs = [self.scanner.Q_id, self.scanner.QBAR_id]
    	
    def circuit_description(self):
        """Check the header for each block exists, and is not misspelled. Call relevant block function."""

        self.previous_block = ""
        # Check if first keyword is a devices
        if (self.symbol.type == self.scanner.KEYWORD 
        	and self.symbol.id == self.scanner.devices_id and self.previous_block == ""):
            print("Entering devices block")
            eofcheck = self.devices_block()

        # If the symbol we expect is any header but we get a bracket, then we can report the header as missing
        elif self.symbol.type == self.scanner.OPEN_BRACKET and self.previous_block == "":
            self.syntax.printerror(self.syntax.NO_HEADER)
            print("Skipping devices block")
            eofcheck = self.skip_block(self.previous_block)
        
        # Incorrect header
        elif self.previous_block == "":
            self.syntax.printerror(self.syntax.HEADER_NAME_ERROR, self.scanner)
            print("Skipping devices block")
            eofcheck = self.skip_block(self.previous_block) 

        # Check if next keyword is initialise
        if (self.symbol.type == self.scanner.KEYWORD 
        	and self.symbol.id == self.scanner.initialise_id and self.previous_block == "devices"):
            print("Entering initialise block")
            eofcheck = self.initialise_block()

        # If the symbol we expect is any header but we get a bracket, then we can report the header as missing
        elif self.symbol.type == self.scanner.OPEN_BRACKET and self.previous_block == "devices":
            self.syntax.printerror(self.syntax.NO_HEADER)
            print("Skipping initialise block")
            eofcheck = self.skip_block(self.previous_block)

        # Incorrect header
        elif self.previous_block == "devices":
            self.syntax.printerror(self.syntax.HEADER_NAME_ERROR, self.scanner)
            print("Skipping initialise block")
            eofcheck = self.skip_block(self.previous_block) 
        
        # Check if next keyword is connections
        if (self.symbol.type == self.scanner.KEYWORD 
        	and self.symbol.id == self.scanner.connections_id and self.previous_block == "initialise"):
            print("Entering connections block")
            eofcheck = self.connections_block()

        # If the symbol we expect is any header but we get a bracket, then we can report the header as missing
        elif self.symbol.type == self.scanner.OPEN_BRACKET and self.previous_block == "initialise":
            self.syntax.printerror(self.syntax.NO_HEADER)
            eofcheck = self.skip_block(self.previous_block)

        # Incorrect header
        elif self.previous_block == "initialise":
            self.syntax.printerror(self.syntax.HEADER_NAME_ERROR, self.scanner)
            eofcheck = self.skip_block(self.previous_block) 
        
        # Check if next keyword is monitors
        if (self.symbol.type == self.scanner.KEYWORD 
        	and self.symbol.id == self.scanner.monitors_id and self.previous_block == "connections"):
            eofcheck = self.monitors_block()

        # If the symbol we expect is any header but we get a bracket, then we can report the header as missing
        elif (self.symbol.type == self.scanner.OPEN_BRACKET and self.previous_block == "connections"):
            self.syntax.printerror(self.syntax.NO_HEADER)
            eofcheck = self.skip_block(self.previous_block)

        # Incorrect header
        elif self.previous_block == "connections":
            self.syntax.printerror(self.syntax.HEADER_NAME_ERROR, self.scanner)
            eofcheck = self.skip_block(self.previous_block) 

        return eofcheck
    
    def skip_block(self, block):
        """Skip entire block and ends up at header of next block, by repeatedly calling skip_line() from the Scanner class.

        For header name errors. We do this because it is not possible to know what is supposed to be inside a block if the header is poorly named. Starts when cursor is on a bad header name. Finishes after having read the first symbol of the next block (header).
        """

        while (self.symbol.id not in self.block_ids and self.symbol.type != self.scanner.EOF):
            self.scanner.skip_line()
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.EOF:
                return True
        
        if block == "":
            self.previous_block = "devices"
        if block == "devices":
            self.previous_block = "initialise"
        if block == "initialise":
            self.previous_block = "connections"

        return False
    
    def devices_block(self):
        """Operate at level of parsing a device block.

        Should finish after reading the first symbol of the next line.
        
        """

        print("Entered device block")

        if self.symbol.type == self.scanner.KEYWORD:
            print("Keyword at start of device block: ", self.names.get_name_string(self.symbol.id))

        # Fetch next symbol after section heading and check it's a bracket
        self.symbol = self.scanner.get_symbol()
        print("Symbol type:", self.scanner.symbol_list[self.symbol.type]) # Bracket
        if self.symbol.type != self.scanner.OPEN_BRACKET:
            # If not a bracket, skip to next character (unique handling method to this error)
            self.syntax.printerror(self.syntax.NO_OPEN_BRACKET, self.scanner)

        print("Checked for open bracket. Fetching next symbol. Expect name.")
        self.previous_block = "devices"

        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.EOF:
            eofcheck = True
            return
        
        # Skip device block, end reached
        if self.symbol.type == self.scanner.CLOSE_BRACKET:
            eofcheck = False
            print("Devices block is empty.")
            return

        # Call line-level function as long as end of block not reached
        while self.symbol.type != self.scanner.CLOSE_BRACKET:
            # Read first name on next line to check if it is a device, switch or clock name
            print("Reading device name inside devices block")
            # Sets name_type and current_name attributes
            self.read_name("devices")
            print("Name type to determine which definition method runs:", self.current_name, self.name_type)
            if self.name_type == "device":
                print("Entering device definition method")
                eofcheck = self.device_definition(self.current_name)
            elif self.name_type == "switch":
                print("Entering switch definition method")
                self.switch_definition(self.current_name)
            elif self.name_type == "clock":
                print("Entering clock definition method")
                self.clock_definition(self.current_name)

            # Read first symbol of next line
            self.symbol = self.scanner.get_symbol()
            print("First symbol of next line: ", self.scanner.symbol_list[self.symbol.type])
            if self.symbol == self.scanner.EOF:
                return True

        self.symbol = self.scanner.get_symbol()
        print("End of device block found using bracket. Setting of checking parameter previous_block:", self.previous_block)
        # Exit the above while loop when symbol stored is a closed bracket
        # End of functionality of devices_block function
        return eofcheck

    def device_definition(self, currentname):
        """Parse one line of device definition.

        Used inside devices block for defining the device names and their corresponding types. Devices are AND, OR, NOR, XOR, NAND, DTYPE only.
        
        It should be read at the point after we have obtained the (expected) first name on each line, and finish without having read the first symbol of the next line.

        Parameters
        -------

        'currentname': the current name read from calling read_name() inside the devices block.
        """

        self.current_name = currentname
        print("Inside device definition method. Current symbol:", self.scanner.symbol_list[self.symbol.type])
        print("Current name: ", self.current_name)
        # Number of different devices initialised on this line
        i = 1

        self.symbol = self.scanner.get_symbol()

        print("First symbol type after device name:", self.scanner.symbol_list[self.symbol.type])
        if self.symbol.type == self.scanner.EOF:
            return True

        while self.symbol.type == self.scanner.COMMA:
            # If comma, expect a device name afterwards
            print("Found a comma, checking for device afterwards")
            # Fetch next thing after comma
            self.symbol = self.scanner.get_symbol()
            # Feed into name reader
            self.read_name("devices")
            print("Symbol type after reading name after comma:", self.scanner.symbol_list[self.symbol.type], self.names.get_name_string(self.symbol.id))
            if self.name_type != "device":
                # If you mix up device types, syntax error
                self.syntax.printerror(self.syntax.INCONSISTENT_DEVICE_NAMES, self.scanner)
            i += 1
            # Get next symbol after device name to check if it's a comma
            self.symbol = self.scanner.get_symbol()
            print("First symbol type after name:", self.scanner.symbol_list[self.symbol.type], self.names.get_name_string(self.symbol.id))

        # If next symbol is definition keyword:
        # Check if symbol type is keyword and symbol ID is that for definition
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id in self.definition_ids:
            
            print("Found definition keyword in right place.")

            # Get next symbol
            self.symbol = self.scanner.get_symbol()
            print("Fetched gate name type. Now checking if it is a valid gate type.")

            # Check if next symbol is gate type id
            if self.symbol.id not in self.gate_type_ids:
                # If symbol is an id but not valid gate type (gate or dtype)
                if self.symbol.id in (self.switch_id or self.clock_id):
                    # Skip to next line and exit function
                    # self.semantic.printerror(self.semantic.WRONG_GATE_FOR_NAME, self.scanner.keywords_list(self.symbol.id),  "AND, OR, NOR, XOR, NAND, or DTYPE")
                    # return
                    print("Semantic error to be implemented")
                    self.scanner.skip_line()
                    return False
                #If symbol is not a valid gate type
                else:
                    self.syntax.printerror(self.syntax.DEVICE_TYPE_ERROR, self.scanner)
            
            # If next symbol is gate type id, append i times the device name to the type list
            # To create a linked list with the device names
            # This should be updated with functionality from the devices class once testing on parser alone is complete
            else:
                self.user_object_type_list += self.scanner.keywords_list[self.symbol.id]*i
                print("Successfully appended device type. Now fetching what should be semicolon.")
                self.symbol = self.scanner.get_symbol()
                print("Symbol in position of semicolon:", self.scanner.symbol_list[self.symbol.type])

                if self.symbol == self.scanner.EOF:
                    return True

                if self.scanner.symbol_list[self.symbol.type] != ";":
                    self.syntax.printerror(self.syntax.NO_SEMICOLON, self.scanner)
                
                return False
        
        # If next symbol is not a definition keyword, throw error        
        else:
            self.syntax.printerror(self.syntax.NO_DEFINITION_KEYWORD, self.scanner)
        
        return False
    
    def switch_definition(self, currentname):
        """Parse one line of switch definition.

        Used inside devices block for defining the switch names and their corresponding types. Switches are SWITCH only.
        
        It should be read at the point after we have obtained the (expected) first name on each line, and finish without having read the first symbol of the next line.

        Parameters
        -------

        'currentname': the current name read from calling read_name() inside the devices block.
        """

        self.current_name = currentname
        print("Inside switch definition method. Current name: ", self.current_name)
        # Number of different devices initialised on this line
        i = 1

        self.symbol = self.scanner.get_symbol()

        print("First symbol type after switch name:", self.scanner.symbol_list[self.symbol.type])
        if self.symbol.type == self.scanner.EOF:
            return True

        while self.symbol.type == self.scanner.COMMA:
            # If comma, expect a device name afterwards
            # Fetch next thing after comma
            self.symbol = self.scanner.get_symbol()
            print("Found a comma, checking for switch afterwards. Symbol type after comma:", self.scanner.symbol_list[self.symbol.type])
            # Feed into name reader
            self.read_name("devices")
            if self.name_type != "switch":
                # If you mix up device types, syntax error
                self.syntax.printerror(self.syntax.INCONSISTENT_DEVICE_NAMES, self.scanner)
            i += 1
            # Get next symbol after device name to check if it's a comma
            self.symbol = self.scanner.get_symbol()
            print("First symbol type after name:", self.scanner.symbol_list[self.symbol.type])

        # If next symbol is definition keyword:
        # Check if symbol type is keyword and symbol ID is that for definition
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id in self.definition_ids:
            
            print("Found definition keyword in right place.")

            # Get next symbol
            self.symbol = self.scanner.get_symbol()
            print("Fetched gate name type. Now checking if it is a valid gate type. Symbol type:", self.scanner.symbol_list[self.symbol.type], self.names.get_name_string(self.symbol.id))

            # Check if next symbol is gate type id
            if self.symbol.id not in self.switch_id:
                # If symbol is an id but not valid gate type (gate or dtype)
                if self.symbol.id in (self.device_ids or self.clock_id):
                    # Skip to next line and exit function
                    # self.semantic.printerror(self.semantic.WRONG_GATE_FOR_NAME, self.scanner.keywords_list(self.symbol.id),  "AND, OR, NOR, XOR, NAND, or DTYPE")
                    # return
                    print("Semantic error to be implemented")
                    self.scanner.skip_line()
                    return False
                #If symbol is not a valid gate type
                else:
                    self.syntax.printerror(self.syntax.DEVICE_TYPE_ERROR, self.scanner)
            
            # If next symbol is gate type id, append i times the device name to the type list
            # To create a linked list with the device names
            # This should be updated with functionality from the devices class once testing on parser alone is complete
            else:
                self.user_object_type_list += self.scanner.keywords_list[self.symbol.id]*i
                print("Successfully appended switch type. Now fetching what should be semicolon.")
                self.symbol = self.scanner.get_symbol()
                print("Symbol in position of semicolon:", self.scanner.symbol_list[self.symbol.type])

                if self.symbol == self.scanner.EOF:
                    return True

                if self.scanner.symbol_list[self.symbol.type] != ";":
                    self.syntax.printerror(self.syntax.NO_SEMICOLON, self.scanner)
                
                return False
        
        # If next symbol is not a definition keyword, throw error        
        else:
            self.syntax.printerror(self.syntax.NO_DEFINITION_KEYWORD, self.scanner)
        
        return False
        
    def clock_definition(self, currentname):
        """Parse one line of clock definition.

        Used inside devices block for defining the clock names and their corresponding types. Clocks are CLOCK only.
        
        It should be read at the point after we have obtained the (expected) first name on each line, and finish without having read the first symbol of the next line.

        Parameters
        -------

        'currentname': the current name read from calling read_name() inside the devices block.
        """

        self.current_name = currentname
        print("Inside clock definition method. Current name: ", self.current_name)
        # Number of different devices initialised on this line
        i = 1

        self.symbol = self.scanner.get_symbol()

        print("First symbol type after switch name:", self.scanner.symbol_list[self.symbol.type])
        if self.symbol.type == self.scanner.EOF:
            return True

        while self.symbol.type == self.scanner.COMMA:
            # If comma, expect a device name afterwards
            # Fetch next thing after comma
            self.symbol = self.scanner.get_symbol()
            print("Found a comma, checking for clock afterwards. Symbol type after comma:", self.scanner.symbol_list[self.symbol.type])
            # Feed into name reader
            self.read_name("devices")
            if self.name_type != "clock":
                # If you mix up device types, syntax error
                self.syntax.printerror(self.syntax.INCONSISTENT_DEVICE_NAMES, self.scanner)
            i += 1
            # Get next symbol after device name to check if it's a comma
            self.symbol = self.scanner.get_symbol()
            print("First symbol type after name:", self.scanner.symbol_list[self.symbol.type])

        # If next symbol is definition keyword:
        # Check if symbol type is keyword and symbol ID is that for definition
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id in self.definition_ids:
            
            print("Found definition keyword in right place.")

            # Get next symbol
            self.symbol = self.scanner.get_symbol()
            print("Fetched gate name type. Now checking if it is a valid gate type. Symbol type:", self.scanner.symbol_list[self.symbol.type], self.names.get_name_string(self.symbol.id))

            # Check if next symbol is clock type id
            if self.symbol.id not in self.clock_id:
                # If symbol is an id but not valid clock type
                if self.symbol.id in (self.device_ids or self.switch_id):
                    # Skip to next line and exit function
                    # self.semantic.printerror(self.semantic.WRONG_GATE_FOR_NAME, self.scanner.keywords_list(self.symbol.id),  "AND, OR, NOR, XOR, NAND, or DTYPE")
                    print("Semantic error to be implemented")
                    self.scanner.skip_line()
                    return False
                #If symbol is not a valid gate type
                else:
                    self.syntax.printerror(self.syntax.DEVICE_TYPE_ERROR, self.scanner)
            
            # If next symbol is gate type id, append i times the device name to the type list
            # To create a linked list with the device names
            # This should be updated with functionality from the devices class once testing on parser alone is complete
            else:
                self.user_object_type_list += self.scanner.keywords_list[self.symbol.id]*i
                print("Successfully appended clock type. Now fetching what should be semicolon.")
                self.symbol = self.scanner.get_symbol()
                print("Symbol in position of semicolon:", self.scanner.symbol_list[self.symbol.type])

                if self.symbol == self.scanner.EOF:
                    return True

                if self.scanner.symbol_list[self.symbol.type] != ";":
                    self.syntax.printerror(self.syntax.NO_SEMICOLON, self.scanner)
                
                return False
        
        # If next symbol is not a definition keyword, throw error        
        else:
            self.syntax.printerror(self.syntax.NO_DEFINITION_KEYWORD, self.scanner)
        
        return False
    
    def read_name(self, block):
        """Read a generic name. Handles case for all devices - gate, dtype, switch and clock.

        It should be called at the point where the first symbol of each line, or the symbol that should be the name, has already been obtained from the scanner.
        
        Parameters
        -------
        
        'block': The block in which this function is called. This is important to check as new device names should not be initialised anywhere other than in the devices block.

        Return current read name.
        """
        print("Entered read name function")

        print("Symbol type:", self.scanner.symbol_list[self.symbol.type])

        # If first symbol is of type NAME (for all gates and DTYPE)
        if self.symbol.type == self.scanner.NAME:
            self.current_name = self.names.names[self.symbol.id]

            print("Current name in read_name() function:", self.current_name)
            self.is_legal_name = True
            self.name_type = ""

            # Check name type - if it's switch 
            if self.current_name[0:2] == "sw":
                print("Checking if valid switch name")
                for i in self.current_name[2:len(self.current_name)]:
                    if not i.isdigit():
                        # Syntax error - invalid name
                        self.syntax.printerror(self.syntax.INCORRECT_SWITCH_NAME, self.scanner)
                        self.is_legal_name = False
                        self.symbol = self.scanner.get_symbol()
                        if self.symbol.type == self.scanner.NAME:
                            self.current_name = self.names.names[self.symbol.id]
                # If error is not thrown:
                self.name_type = "switch"
                print("Switch found. Name type:", self.name_type)

            # Check name type - if it's clock
            elif self.current_name[0:3] == "clk":
                for i in self.current_name[3:len(self.current_name)]:
                    if not i.isdigit():
                        # Syntax error - invalid name
                        self.syntax.printerror(self.syntax.INCORRECT_CLOCK_NAME, self.scanner)
                        self.is_legal_name = False
                        # If we skip a line, I want the names() function to store the next name as the one on the next line down
                        self.symbol = self.scanner.get_symbol()
                        if self.symbol.type == self.scanner.NAME:
                            self.current_name = self.names.names[self.symbol.id]
                # If error is not thrown:
                print("Clock found")
                self.name_type = "clock"

            # Check if all letters in device name are lowercase
            else:
                for i in self.current_name:
                    if i.isalpha():
                        if i.isupper():
                            self.syntax.printerror(self.syntax.DEVICE_LETTER_CAPITAL, self.scanner)
                            self.is_legal_name = False
                            self.symbol = self.scanner.get_symbol()
                            if self.symbol.type == self.scanner.NAME:
                                self.current_name = self.names.names[self.symbol.id]
                # If error is not thrown:
                self.name_type = "device"

            # If block is devices block
            if block == "devices":
                # If name is legal and does not exist in list yet, append to name list
                if self.is_legal_name and self.current_name not in self.user_object_name_list:
                    self.user_object_name_list.append(self.current_name)
                    return 
                # If trying to initialise a device using existing name, throw semantic error
                elif self.is_legal_name and self.current_name in self.user_object_name_list:
                    # self.semantic.printerror(self.semantic.NAME_ALREADY_EXISTS, self.current_name)
                    self.scanner.skip_line()
                    return
            
            # If block is initialise block
            if block == "initialise":
                # If name is legal and does not exist in list yet, throw semantic error
                if self.is_legal_name and self.current_name not in self.user_object_name_list:
                    self.scanner.skip_line()
                    return
                # Parse existing name
                elif self.is_legal_name and self.current_name in self.user_object_name_list:
                    return 
        
        # No device name found at the beginning of the line inside the device class but not reached end of block yet
        elif self.symbol.id != self.scanner.CLOSE_BRACKET and self.symbol.type != self.scanner.NAME:
            self.syntax.printerror(self.syntax.NO_DEVICE_NAME, self.scanner)
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.NAME:
                self.current_name = self.names.names[self.symbol.id]
    
    def parse_network(self):
        """Parse the circuit definition file."""

        self.eofcheck = False
        self.symbol = self.scanner.get_symbol()
        # Tree structure: split into blocks
        self.eofcheck = self.circuit_description()

        if self.eofcheck == True:
            print("end of file reached")
            self.scanner.file.close()

        return
    
    def initialise_block(self):
        """Initialises devices, switches and clocks.
        
        Devices are given input number. Switches are given high or low at start. Clocks are given a cycle length.
        """
        self.previous_block == "initialise"
    
       def connections_block(self):
        self.previous_block == "connections"

    def monitors_block(self):
        return None
    def gate_initialisation(self):
        """Parse one line inside initialise block specific to gates.
        
        Starts at point where the first symbol has already been read and is confirmed to be a device type name.
        """
    
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