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

        # names class object
        self.names = names
        self.devices = devices
        self.network = network
        self.scanner = scanner
        self.monitors = monitors
        self.syntax = SyntaxError()
        self.semantic = SemanticError()

        # Required to store names and type associated with each name, since make_device() is only called in the initialisation section
        self.object_dict = {}

        # Dictionary for device kind. Used in Device.make_device()
        self.device_kind_dict = {"XOR": self.devices.XOR, "AND": self.devices.AND, "OR": self.devices.OR, "NOR": self.devices.NOR, "NAND": self.devices.NAND, "DTYPE": self.devices.D_TYPE, "SWITCH": self.devices.SWITCH, "CLOCK": self.devices.CLOCK}

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
    	
        self.bracket_count = 0

    def circuit_description(self):
        """Check the header for each block exists, and is not misspelled. Call relevant block function."""

        self.previous_block = ""
        # Check if first keyword is a devices
        if (self.symbol.type == self.scanner.KEYWORD 
        	and self.symbol.id == self.scanner.devices_id and self.previous_block == ""):
            print("Entering devices block")
            eofcheck = self.devices_block()
            if eofcheck == True:
                return eofcheck

        # If the symbol we expect is any header but we get a bracket, then we can report the header as missing
        elif self.symbol.type == self.scanner.OPEN_BRACKET and self.previous_block == "":
            self.syntax.printerror(self.syntax.NO_HEADER)
            print("Skipping devices block")
            eofcheck = self.skip_block(self.previous_block)
            if eofcheck == True:
                return eofcheck
        # Incorrect header
        elif self.previous_block == "":
            self.syntax.printerror(self.syntax.HEADER_NAME_ERROR, self.scanner)
            print("Skipping devices block")
            eofcheck = self.skip_block(self.previous_block) 
            if eofcheck == True:
                return eofcheck

        # Check if next keyword is initialise
        if (self.symbol.type == self.scanner.KEYWORD 
        	and self.symbol.id == self.scanner.initialise_id and self.previous_block == "devices"):
            print("Entering initialise block")
            eofcheck = self.initialise_block()
            if eofcheck == True:
                return eofcheck

        # If the symbol we expect is any header but we get a bracket, then we can report the header as missing
        elif self.symbol.type == self.scanner.OPEN_BRACKET and self.previous_block == "devices":
            self.syntax.printerror(self.syntax.NO_HEADER)
            print("Skipping initialise block")
            eofcheck = self.skip_block(self.previous_block)
            if eofcheck == True:
                return eofcheck

        # Incorrect header
        elif self.previous_block == "devices":
            self.syntax.printerror(self.syntax.HEADER_NAME_ERROR, self.scanner)
            print("Skipping initialise block")
            eofcheck = self.skip_block(self.previous_block) 
            if eofcheck == True:
                return eofcheck

        # Check if next keyword is connections
        if (self.symbol.type == self.scanner.KEYWORD 
        	and self.symbol.id == self.scanner.connections_id and self.previous_block == "initialise"):
            print("Entering connections block")
            eofcheck = self.connections_block()
            if eofcheck == True:
                return eofcheck

        # If the symbol we expect is any header but we get a bracket, then we can report the header as missing
        elif self.symbol.type == self.scanner.OPEN_BRACKET and self.previous_block == "initialise":
            self.syntax.printerror(self.syntax.NO_HEADER)
            eofcheck = self.skip_block(self.previous_block)
            if eofcheck == True:
                return eofcheck

        # Incorrect header
        elif self.previous_block == "initialise":
            self.syntax.printerror(self.syntax.HEADER_NAME_ERROR, self.scanner)
            eofcheck = self.skip_block(self.previous_block) 
            if eofcheck == True:
                return eofcheck

        # Check if next keyword is monitors
        if (self.symbol.type == self.scanner.KEYWORD 
        	and self.symbol.id == self.scanner.monitors_id and self.previous_block == "connections"):
            eofcheck = self.monitors_block()
            if eofcheck == True:
                return eofcheck

        # If the symbol we expect is any header but we get a bracket, then we can report the header as missing
        elif (self.symbol.type == self.scanner.OPEN_BRACKET and self.previous_block == "connections"):
            self.syntax.printerror(self.syntax.NO_HEADER)
            eofcheck = self.skip_block(self.previous_block)
            if eofcheck == True:
                return eofcheck

        # Incorrect header
        elif self.previous_block == "connections":
            self.syntax.printerror(self.syntax.HEADER_NAME_ERROR, self.scanner)
            eofcheck = self.skip_block(self.previous_block) 
            if eofcheck == True:
                return eofcheck

        return True
    
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

        eofcheck = False

        if self.symbol.type == self.scanner.KEYWORD:
            print("Keyword at start of device block: ", self.names.get_name_string(self.symbol.id))

        # Fetch next symbol after section heading and check it's a bracket
        self.symbol = self.scanner.get_symbol()
        print("Symbol type after bracket:", self.scanner.symbol_list[self.symbol.type]) # Bracket
        if self.symbol.type != self.scanner.OPEN_BRACKET:
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
        while self.symbol.type != self.scanner.CLOSE_BRACKET and self.symbol.id not in self.block_ids:
            # Read first name on next line to check if it is a device, switch or clock name
            print("Reading device name inside devices block")
            # Sets name_type and current_name attributes
            self.read_name("devices")
            # Error recovery: for if first name on each line is not valid
            while self.is_legal_name == False:
                # Get next symbol on next line but also check it's not a close bracket
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type == self.scanner.CLOSE_BRACKET:
                    # Get next section header and return
                    self.symbol = self.scanner.get_symbol()
                    return False
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

        if self.symbol.type == self.scanner.CLOSE_BRACKET:
            self.bracket_count += 1

            # Get symbol after close bracket
            self.symbol = self.scanner.get_symbol()
            
            print("End of device block found using bracket. Setting of checking parameter previous_block:", self.previous_block)
            # Exit the above while loop when symbol stored is a closed bracket
            # End of functionality of devices_block function
            return eofcheck

        # Expect to be reading a block header if missing close bracket
        else:
            self.syntax.printerror(self.syntax.NO_CLOSE_BRACKET)
            return eofcheck

    def initialise_block(self):
        """Initialises devices, switches and clocks.
        
        Devices are given input number. Switches are given high or low at start. Clocks are given a cycle length.
        """
        print("Entered initialise block")

        if self.symbol.type == self.scanner.KEYWORD:
            print("Keyword at start of initialise block: ", self.names.get_name_string(self.symbol.id))

        # Fetch next symbol after section heading and check it's a bracket
        self.symbol = self.scanner.get_symbol()
        print("Symbol type:", self.scanner.symbol_list[self.symbol.type]) # Bracket
        if self.symbol.type != self.scanner.OPEN_BRACKET:
            self.syntax.printerror(self.syntax.NO_OPEN_BRACKET, self.scanner)

        print("Checked for open bracket. Fetching next symbol. Expect name.")
        self.previous_block = "initialise"

        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.EOF:
            eofcheck = True
            return eofcheck
        # Skip device block, end reached
        if self.symbol.type == self.scanner.CLOSE_BRACKET:
            eofcheck = False
            print("Devices block is empty.")
            return eofcheck

        # Call line-level function as long as end of block not reached
        while self.symbol.type != self.scanner.CLOSE_BRACKET and self.symbol.id not in self.block_ids:
            # Read first name on next line to check if it is a device, switch or clock name
            # Sets name_type and current_name attributes
            self.read_name("initialise")
            print("Device name read inside initialise block as:", self.current_name)
            # Error recovery: for if first name on each line is not valid
            while self.is_legal_name == False:
                # Get next symbol on next line but also check it's not a close bracket
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type == self.scanner.CLOSE_BRACKET:
                    # Get next section header and return
                    self.symbol = self.scanner.get_symbol()
                    return False
                self.read_name("initialise")
                print("Device name read inside initialise block as:", self.current_name)

            print("Name type to determine which initialisation method runs:", self.current_name, self.name_type)
            if self.name_type == "device":
                print("Entering device initialisation method")
                eofcheck = self.device_initialisation(self.current_name)
            elif self.name_type == "switch":
                print("Entering switch initialisation method")
                self.switch_initialisation(self.current_name)
            elif self.name_type == "clock":
                print("Entering clock initialisation method")
                self.clock_initialisation(self.current_name)

            # Read first symbol of next line
            self.symbol = self.scanner.get_symbol()
            print("First symbol of next line: ", self.scanner.symbol_list[self.symbol.type])
            if self.symbol == self.scanner.EOF:
                return True

        self.symbol = self.scanner.get_symbol()
        print("End of device block found using bracket. Setting of checking parameter previous_block:", self.previous_block)
        # Exit the above while loop when symbol stored is a closed bracket
        # End of functionality of devices_block function
        return False

    def connections_block(self):
        """Operate at level of parsing a device block.

        Should finish after reading the first symbol of the next line.
        
        """

        print("Entered connections block")
        print("State of object dictionary: ", self.object_dict)
        return True  

#===========================================================================================================
#===========================================================================================================

    def device_definition(self, currentname):
        """Parse one line of device definition.

        Used inside devices block for defining the device names and their corresponding types. Devices are AND, OR, NOR, XOR, NAND, DTYPE only.
        
        It should be read at the point after we have obtained the (expected) first name on each line, and finish without having read the first symbol of the next line.

        Parameters
        -------

        'currentname': the current name read from calling read_name() inside the devices block.
        """

        self.current_name = currentname
        devices_to_add = [currentname]
        
        print("Inside device definition method. Current symbol:", self.scanner.symbol_list[self.symbol.type])
        print("Current name: ", self.current_name)

        self.symbol = self.scanner.get_symbol()

        print("First symbol type after device name:", self.scanner.symbol_list[self.symbol.type])
        if self.symbol.type == self.scanner.EOF:
            return True

        while self.symbol.type == self.scanner.COMMA:
            # If comma, expect a device name afterwards
            # Fetch next thing after comma
            self.symbol = self.scanner.get_symbol()
            # Feed into name reader
            self.read_name("devices")
            # Append to list at top of this method
            devices_to_add.append(self.current_name)
            print("Symbol type after reading name after comma:", self.scanner.symbol_list[self.symbol.type], self.names.get_name_string(self.symbol.id))
            
            if self.name_type != "device":
                # If you mix up device types, syntax error
                self.syntax.printerror(self.syntax.INCONSISTENT_DEVICE_NAMES, self.scanner)

            # Get next symbol after device name to check if it's a comma
            self.symbol = self.scanner.get_symbol()

        # If next symbol is definition keyword:
        # Check if symbol type is keyword and symbol ID is that for definition
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id in self.definition_ids:

            # Get next symbol
            self.symbol = self.scanner.get_symbol()

            # Check if next symbol is gate type id
            if self.symbol.id not in self.gate_type_ids:
                # If symbol is an id but not valid gate type (gate or dtype)
                if self.symbol.id in (self.switch_id or self.clock_id):
                    # Skip to next line and exit function
                    self.semantic.printerror(self.semantic.WRONG_GATE_FOR_NAME, self.scanner.keywords_list(self.symbol.id),  "AND, OR, NOR, XOR, NAND, or DTYPE")
                    return False
                #If symbol is not a valid gate type
                else:
                    self.syntax.printerror(self.syntax.DEVICE_TYPE_ERROR, self.scanner)
            
            # If next symbol is gate type id, add to dictionary
            # For testing purposes, also append to list in Parse class
            else:
                for device in devices_to_add:
                    self.object_dict[device] = self.names.get_name_string(self.symbol.id)
                print("Successfully appended device type {}".format(self.names.get_name_string(self.symbol.id)))
                self.symbol = self.scanner.get_symbol()

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
        devices_to_add = [currentname]

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
            devices_to_add.append(self.current_name)
            if self.name_type != "switch":
                # If you mix up device types, syntax error
                self.syntax.printerror(self.syntax.INCONSISTENT_DEVICE_NAMES, self.scanner)
            # Get next symbol after device name to check if it's a comma
            self.symbol = self.scanner.get_symbol()

        # If next symbol is definition keyword:
        # Check if symbol type is keyword and symbol ID is that for definition
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id in self.definition_ids:
            
            print("Found definition keyword in right place.")

            # Get next symbol
            self.symbol = self.scanner.get_symbol()
            print("Fetched gate name type. Now checking if it is a valid gate type. Symbol type:", self.scanner.symbol_list[self.symbol.type], self.names.get_name_string(self.symbol.id))

            # Check if next symbol is gate type id
            if self.symbol.id not in self.switch_id:
                # If symbol is an id but not valid gate type 
                if self.symbol.id in (self.device_ids or self.clock_id):
                    # Skip to next line and exit function
                    self.semantic.printerror(self.semantic.WRONG_GATE_FOR_NAME, self.scanner.keywords_list(self.symbol.id),  "SWITCH")
                    return False
                #If symbol is not a valid gate type
                else:
                    self.syntax.printerror(self.syntax.DEVICE_TYPE_ERROR, self.scanner)
            
            else:
                for device in devices_to_add:
                    self.object_dict[device] = "SWITCH"
                print("Successfully appended switch type. Now fetching what should be semicolon.")
                self.symbol = self.scanner.get_symbol()

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
        devices_to_add = [currentname]

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
            if self.is_legal_name == False:
                return False
            devices_to_add.append(self.current_name)
            if self.name_type != "clock":
                # If you mix up device types, syntax error
                self.syntax.printerror(self.syntax.INCONSISTENT_DEVICE_NAMES, self.scanner)
            i += 1
            # Get next symbol after device name to check if it's a comma
            self.symbol = self.scanner.get_symbol()

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
                    self.semantic.printerror(self.semantic.WRONG_GATE_FOR_NAME, self.scanner.keywords_list(self.symbol.id),  "CLOCK")
                    return False
                #If symbol is not a valid gate type
                else:
                    self.syntax.printerror(self.syntax.DEVICE_TYPE_ERROR, self.scanner)
            
            else:
                for device in devices_to_add:
                    self.object_dict[device] = "CLOCK"
                print("Successfully appended clock type. Now fetching what should be semicolon.")
                self.symbol = self.scanner.get_symbol()

                if self.symbol == self.scanner.EOF:
                    return True

                if self.scanner.symbol_list[self.symbol.type] != ";":
                    self.syntax.printerror(self.syntax.NO_SEMICOLON, self.scanner)
                
                return False
        
        # If next symbol is not a definition keyword, throw error        
        else:
            self.syntax.printerror(self.syntax.NO_DEFINITION_KEYWORD, self.scanner)
            return False
        return False

#===========================================================================================================
#===========================================================================================================

    def read_name(self, block):
        """Read a generic name and saves it to self.current_name, as well as the type to self.name_type. Handles case for all devices - gate, dtype, switch and clock.

        Handles syntax errors for where a valid name is expected but not given, and incorrect switch and clock names. Handles semantic errors for devices already named (for definitions) or devices not already named (for initialise, connections). 
        It should be called at the point where the first symbol of each line, or the symbol that should be the name, has already been obtained from the scanner. The next symbol is never obtained at any point in this method.
        
        Parameters
        -------
        
        'block': The block in which this function is called. This is important to check as new device names should not be initialised anywhere other than in the devices block.

        Return current read name.
        """
        print("Entered read name function in block {}".format(block))

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
                # If error is not thrown:
                self.name_type = "device"

            # If block is devices block
            if block == "devices" and self.is_legal_name:
                # If name is legal and does not exist in list yet, append to name list and call Device() to create device
                if self.current_name not in self.object_dict:
                    return 
                # If trying to initialise a device using existing name, throw semantic error
                elif self.current_name in self.object_dict:
                    self.is_legal_name = False
                    self.semantic.printerror(self.semantic.NAME_ALREADY_EXISTS, self.scanner, self.current_name)
                    return
            
            # If block is initialise block
            if block == "initialise":
                # If name is legal and does not exist in list yet, throw semantic error
                if self.is_legal_name and self.current_name not in self.object_dict:
                    self.is_legal_name = False
                    self.semantic.printerror(self.semantic.NAME_FOR_INITIALISE_NOT_DEFINED, self.scanner, self.current_name)
                    return
                elif self.is_legal_name and self.current_name in self.object_dict:
                    return
            
            # If block is connections block
            if block == "connections":
                # If name is legal and does not exist in list yet, throw semantic error
                if self.is_legal_name and self.current_name not in self.object_dict:
                    self.is_legal_name = False
                    self.semantic.printerror(self.semantic.NAME_FOR_CONNECTIONS_NOT_DEFINED, self.scanner, self.current_name)
                    return
                elif self.is_legal_name and self.current_name in self.object_dict:
                # Don't return anything - whole point is to update current name
                    return 
        
        # No device name found at the beginning of the line inside the device class but not reached end of block yet
        elif self.symbol.id != self.scanner.CLOSE_BRACKET and self.symbol.type != self.scanner.NAME:
            self.syntax.printerror(self.syntax.NO_DEVICE_NAME, self.scanner)
            self.is_legal_name = False
            return
    
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

#===========================================================================================================
#===========================================================================================================

    def device_initialisation(self, currentname):
        """Parse one line of device initialisation.

        Used inside initialise block for defining the number of inputs, switch initial values and clock cycle lengths. Devices are AND, OR, NOR, XOR, NAND, DTYPE only. It should be read at the point after we have obtained the (expected) first name on each line, and finish without having read the first symbol of the next line.

        Parameters
        -------

        'currentname': the current name read from calling read_name() inside the devices block.
        """

        # Store names of devices to be initialised
        devices_to_be_initialised = [currentname]

        self.current_name = currentname
        print("Inside device initialisation method. Current symbol:", self.scanner.symbol_list[self.symbol.type])
        print("Current name: ", self.current_name)

        # Get expected comma
        self.symbol = self.scanner.get_symbol()

        print("First symbol type after device name:", self.scanner.symbol_list[self.symbol.type])
        if self.symbol.type == self.scanner.EOF:
            return True

        while self.symbol.type == self.scanner.COMMA:
            # If comma, expect a device name afterwards
            # Fetch next thing after comma
            self.symbol = self.scanner.get_symbol()
            
            # Feed into name reader. ALWAYS check that if the name is not legal, skip the rest of the function as error.
            self.read_name("initialise")
            if self.is_legal_name == False:
                return

            devices_to_be_initialised.append(self.current_name)
            if self.name_type != "device":
                # If you mix up device types, syntax error
                self.syntax.printerror(self.syntax.INCONSISTENT_DEVICE_NAMES, self.scanner)
                return False
            # Get next symbol after device name to check if it's a comma
            self.symbol = self.scanner.get_symbol()

        # If next symbol is definition keyword:
        # Check if symbol type is keyword and symbol ID is that for definition
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id in self.possession_ids:
            
            # Get next symbol
            self.symbol = self.scanner.get_symbol()

            # Check if next symbol is number
            if self.symbol.type != self.scanner.NUMBER:
                self.syntax.printerror(self.syntax.INPUT_NUMBER_ERROR, self.scanner)
                return False
            else:
                # Get number
                temp_inputs = self.symbol.id
                print("Checking devices dictionary at this point", self.object_dict)
                # Fetch and check what should be 'input' or 'inputs'
                self.symbol = self.scanner.get_symbol()
                if self.symbol.id not in self.other_keywords_ids[2:4]:
                    self.syntax.printerror(self.syntax.INPUTS_KEYWORD_ERROR)
                    return False
                # If next symbol says 'input' or 'input', update the relevant attributes
                else:
                    for device in devices_to_be_initialised:
                        # Make device: args device_id, device_kind, input number
                        self.devices.make_device(self.names.query(device), self.device_kind_dict[self.object_dict[device]], temp_inputs)

                    # Get expected semicolon
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol == self.scanner.EOF:
                        return True
                    if self.scanner.symbol_list[self.symbol.type] != ";":
                        self.syntax.printerror(self.syntax.NO_SEMICOLON, self.scanner)
                        return False
                    return False
        
        # If next symbol is not a possession keyword, throw error        
        else:
            self.syntax.printerror(self.syntax.NO_POSSESSION_KEYWORD, self.scanner)
            return False
    
    def switch_initialisation(self, currentname):
        """Parse one line of switch initialisation.

        Used inside initialise block for defining switch initial values. Switches are SWITCH only. It should be read at the point after we have obtained the (expected) first name on each line, and finish without having read the first symbol of the next line.

        Parameters
        -------

        'currentname': the current name read from calling read_name() inside the devices block.
        """
        
        # List of switch names to initialise
        switches_to_be_initialised = [currentname]

        self.current_name = currentname
        print("Inside switch initialisation method. Current symbol:", self.scanner.symbol_list[self.symbol.type])

        self.symbol = self.scanner.get_symbol()

        print("First symbol type after device name:", self.scanner.symbol_list[self.symbol.type])
        if self.symbol.type == self.scanner.EOF:
            return True

        while self.symbol.type == self.scanner.COMMA:
            # If comma, expect a device name afterwards
            # Fetch next thing after comma
            self.symbol = self.scanner.get_symbol()
            # Feed into name reader
            self.read_name("initialise")
            switches_to_be_initialised.append(self.current_name)
            if self.name_type != "switch":
                # If you mix up device types, syntax error
                self.syntax.printerror(self.syntax.INCONSISTENT_DEVICE_NAMES, self.scanner)
            # Get next symbol after device name to check if it's a comma
            self.symbol = self.scanner.get_symbol()

        # If next symbol is definition keyword:
        # Check if symbol type is keyword and symbol ID is that for definition
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id in self.definition_ids:
            
            # Get next symbol
            self.symbol = self.scanner.get_symbol()
            
            # Check if next symbol is switch level
            if self.symbol.id not in self.switch_level:
                self.syntax.printerror(self.syntax.SWITCH_LEVEL_ERROR, self.scanner)

            else:
                # Set switch state property for object in Device class
                # String, capitalised
                for switch in switches_to_be_initialised:
                    # Make device: args device_id, device_kind, switch level
                    self.devices.make_device(self.names.query(switch), self.devices.SWITCH, self.scanner.keywords_list[self.symbol.id])

                print("Successfully added switch levels. Now fetching what should be semicolon.")
                self.symbol = self.scanner.get_symbol()
                if self.symbol == self.scanner.EOF:
                    return True
                if self.scanner.symbol_list[self.symbol.type] != ";":
                    self.syntax.printerror(self.syntax.NO_SEMICOLON, self.scanner)
                
                return False
        
        # If next symbol is not a possession keyword, throw error        
        else:
            self.syntax.printerror(self.syntax.NO_DEFINITION_KEYWORD, self.scanner)
        
        return False
    
    def clock_initialisation(self, currentname):
        """Parse one line of clock initialisation.

        Used inside initialise block for defining clock cycle length. clocks are CLOCK only. It should be read at the point after we have obtained the (expected) first name on each line, and finish without having read the first symbol of the next line.

        Parameters
        -------

        'currentname': the current name read from calling read_name() inside the devices block.
        """

        self.current_name = currentname
        print("Inside clock initialisation method. Current symbol:", self.scanner.symbol_list[self.symbol.type])

        self.symbol = self.scanner.get_symbol()

        print("First symbol type after device name:", self.scanner.symbol_list[self.symbol.type])
        if self.symbol.type == self.scanner.EOF:
            return True

        # If next symbol is 'cycle' keyword
        # Check if symbol type is keyword and symbol ID is that for definition
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.other_keywords_ids[4]:
            
            # Get next symbol
            self.symbol = self.scanner.get_symbol()
            
            # Check if next symbol 'length' keyword
            if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.other_keywords_ids[5]:
                
                # Get next symbol - should be number
                self.symbol = self.scanner.get_symbol()
                
                if self.symbol.type == self.scanner.NUMBER:
                    
                    # Check that number is >0
                    if self.symbol.id <= 0:
                        self.semantic.printerror(self.semantic.NEGATIVE_NUMBER_ILLEGAL)

                    # Make and initialise clock device
                    self.devices.make_device(self.names.query(self.current_name), self.devices.CLOCK, int(self.symbol.id/2))

                    print("Successfully added clock cycle length. Now fetching what should be semicolon.")
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol == self.scanner.EOF:
                        return True
                    if self.scanner.symbol_list[self.symbol.type] != ";":
                        self.syntax.printerror(self.syntax.NO_SEMICOLON, self.scanner)
                    
                    return False
                
                else:
                    self.syntax.printerror(self.syntax.NO_CYCLE_LENGTH, self.scanner)

            else:
                self.syntax.printerror(self.syntax.NO_LENGTH_KEYWORD, self.scanner)
        
        # If next symbol is not a possession keyword, throw error        
        else:
            self.syntax.printerror(self.syntax.NO_CYCLE_KEYWORD, self.scanner)
        
        return False
    
    def gate_input_name(self):
        print("some gate input name stuff")
        return
                
    def dtype_input_name(self):
        print("Some dtype input name stuff")	
        return