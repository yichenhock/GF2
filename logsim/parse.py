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
        self.signal_names = []

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
        """Check the header for each block exists, that it is not misspelled and call the relevant block function."""

        self.previous_block = ""
        # Check if first keyword is a devices
        if (self.symbol.type == self.scanner.KEYWORD 
        	and self.symbol.id == self.scanner.devices_id and self.previous_block == ""):
            eofcheck = self.devices_block()
            if eofcheck == True:
                return eofcheck

        # If the symbol we expect is any header but we get a bracket, then we can report the header as missing
        elif self.symbol.type == self.scanner.OPEN_BRACKET and self.previous_block == "":
            self.syntax.printerror(self.syntax.NO_HEADER, self.scanner)
            print("Skipping devices block")
            eofcheck = self.skip_block(self.previous_block)
            if eofcheck == True:
                return eofcheck

        # Incorrect header
        elif self.previous_block == "":
            if self.symbol.id in [self.scanner.initialise_id, self.scanner.connections_id, self.scanner.monitors_id]:
                self.syntax.printerror(self.syntax.MISSING_SECTION, "initialise")
            else:
                self.syntax.printerror(self.syntax.HEADER_NAME_ERROR, self.scanner)
            print("Skipping devices block")
            eofcheck = self.skip_block(self.previous_block) 
            if eofcheck == True:
                return eofcheck

        # Check if next keyword is initialise
        if (self.symbol.type == self.scanner.KEYWORD 
        	and self.symbol.id == self.scanner.initialise_id and self.previous_block == "devices"):
            eofcheck = self.initialise_block()
            if eofcheck == True:
                return eofcheck

        # If the symbol we expect is any header but we get a bracket, then we can report the header as missing
        elif self.symbol.type == self.scanner.OPEN_BRACKET and self.previous_block == "devices":
            self.syntax.printerror(self.syntax.NO_HEADER, self.scanner)

            eofcheck = self.skip_block(self.previous_block)
            if eofcheck == True:
                return eofcheck

        # Incorrect header
        elif self.previous_block == "devices":
            if self.symbol.id in [self.scanner.connections_id, self.scanner.monitors_id]:
                self.syntax.printerror(self.syntax.MISSING_SECTION, "initialise")
            else:
                self.syntax.printerror(self.syntax.HEADER_NAME_ERROR, self.scanner)
            print("Skipping initialise block")
            eofcheck = self.skip_block(self.previous_block) 
            if eofcheck == True:
                return eofcheck

        # Check if next keyword is connections
        if (self.symbol.type == self.scanner.KEYWORD 
        	and self.symbol.id == self.scanner.connections_id and self.previous_block == "initialise"):
            eofcheck = self.connections_block()
            if eofcheck == True:
                return eofcheck

        # If the symbol we expect is any header but we get a bracket, then we can report the header as missing
        elif self.symbol.type == self.scanner.OPEN_BRACKET and self.previous_block == "initialise":
            self.syntax.printerror(self.syntax.NO_HEADER, self.scanner)
            print("Skipping connections block")
            eofcheck = self.skip_block(self.previous_block)
            if eofcheck == True:
                return eofcheck

        # Incorrect header
        elif self.previous_block == "initialise":
            if self.symbol.id == self.scanner.monitors_id:
                print("User opted to not include connections block.")
            else:
                self.syntax.printerror(self.syntax.HEADER_NAME_ERROR, self.scanner)
            print("Skipping connections block.")
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
            self.syntax.printerror(self.syntax.NO_HEADER, self.scanner)
            eofcheck = self.skip_block(self.previous_block)
            if eofcheck == True:
                return eofcheck

        # Incorrect header
        elif self.previous_block == "connections":
            if self.symbol.id == self.scanner.monitors_id:
                print("User opted to not include monitors block.")
            else:
                self.syntax.printerror(self.syntax.HEADER_NAME_ERROR, self.scanner)
            eofcheck = self.skip_block(self.previous_block) 
            if eofcheck == True:
                return eofcheck

        return True

#===========================================================================================================
#===========================================================================================================

    def devices_block(self):
        """Operate at level of parsing a device block.

        Finish after reading the first symbol of the next line.
        
        """

        print("Entered device block")

        eofcheck = False

        # Fetch next symbol after section heading and check it's a bracket
        self.symbol = self.scanner.get_symbol()

        if self.symbol.type != self.scanner.OPEN_BRACKET:
            self.syntax.printerror(self.syntax.NO_OPEN_BRACKET, self.scanner)
        
        self.previous_block = "devices"

        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.EOF:
            eofcheck = True
            return
        
        # Skip device block, end reached
        if self.symbol.type == self.scanner.CLOSE_BRACKET:
            eofcheck = False
            print("Devices block is empty.")
            self.symbol = self.scanner.get_symbol()
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

            if self.symbol == self.scanner.EOF:
                return True

        if self.symbol.type == self.scanner.CLOSE_BRACKET:
            self.symbol = self.scanner.get_symbol()
            return eofcheck

        # Expect to be reading a block header if missing close bracket
        else:
            self.syntax.printerror(self.syntax.NO_CLOSE_BRACKET, self.scanner)
            return eofcheck

    def initialise_block(self):
        """Initialise devices, switches and clocks.
        
        Devices are given input number. Switches are given high or low at start. Clocks are given a cycle length.
        """
        print("Entered initialise block")

        # Fetch next symbol after section heading and check it's a bracket
        self.symbol = self.scanner.get_symbol()

        if self.symbol.type != self.scanner.OPEN_BRACKET:
            self.syntax.printerror(self.syntax.NO_OPEN_BRACKET, self.scanner)

        self.previous_block = "initialise"

        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.EOF:
            eofcheck = True
            return eofcheck
        # Skip device block, end reached
        if self.symbol.type == self.scanner.CLOSE_BRACKET:
            eofcheck = False
            print("Devices block is empty.")
            self.symbol = self.scanner.get_symbol()
            return eofcheck

        # Call line-level function as long as end of block not reached
        while self.symbol.type != self.scanner.CLOSE_BRACKET and self.symbol.id not in self.block_ids:
            # Read first name on next line to check if it is a device, switch or clock name
            # Sets name_type and current_name attributes
            self.read_name("initialise")
            # Error recovery: for if first name on each line is not valid
            while self.is_legal_name == False:
                # Get next symbol on next line but also check it's not a close bracket
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type == self.scanner.CLOSE_BRACKET:
                    # Get next section header and return
                    self.symbol = self.scanner.get_symbol()
                    return False
                self.read_name("devices")

            # Error recovery: for if first name on each line is not valid
            while self.is_legal_name == False:
                # Get next symbol on next line but also check it's not a close bracket
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type == self.scanner.CLOSE_BRACKET:
                    # Get next section header and return
                    self.symbol = self.scanner.get_symbol()
                    return False
                self.read_name("initialise")

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

            if self.symbol == self.scanner.EOF:
                return True

        if self.symbol.type == self.scanner.CLOSE_BRACKET:
            self.symbol = self.scanner.get_symbol()
            return False
        else:
            self.syntax.printerror(self.syntax.NO_CLOSE_BRACKET, self.scanner)
            return False

    def connections_block(self):
        """Operate at level of parsing a device block.

        Finish after reading the first symbol of the next line.
        
        """

        print("============================================Entered connections block")

        # Fetch next symbol after section heading and check it's a bracket
        self.symbol = self.scanner.get_symbol()

        if self.symbol.type != self.scanner.OPEN_BRACKET:
            self.syntax.printerror(self.syntax.NO_OPEN_BRACKET, self.scanner)

        print("Checked for open bracket. Fetching next symbol. Expect device name subheader.")
        self.previous_block = "connections"

        # Fetch name subheader
        self.symbol = self.scanner.get_symbol()
        
        # Skip device block, end reached
        if self.symbol.type == self.scanner.CLOSE_BRACKET:
            print("Connections block is empty.")
            self.symbol = self.scanner.get_symbol()
            return False

        # Outer while loop for different device subsections
        while self.symbol.type != self.scanner.CLOSE_BRACKET and self.symbol.id not in self.block_ids:

            # Read connection sub-block subheading
            self.read_name("connections subheading")
            eofcheck = self.connections_sub_block()
            if eofcheck: # If missing close bracket in subsection, parser refuses to read and sees end of file
                return True
            # Add error recovery for if read_name does not return a proper name
        
        # If for whatever reason we end up at a close bracket, get next symbol (subheader)
        if self.symbol.type == self.scanner.CLOSE_BRACKET:
            # Get symbol after close bracket
            self.symbol = self.scanner.get_symbol()  
            print("End of connections block found using bracket. Setting of checking parameter previous_block:", self.previous_block)
            return False
        else:
            self.syntax.printerror(self.syntax.NO_CLOSE_BRACKET, self.scanner)
            return False

    def monitors_block(self):
        """Operate at level of parsing a monitor block.

        Finish after reading the first symbol of the next line.
        
        """

        print("Entered monitors block=========================================")
        # Saves a list of signal names as in Devices class
        self.monitors_to_add = []
        # Fetch next symbol after section heading and check it's a bracket
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type != self.scanner.OPEN_BRACKET:
            self.syntax.printerror(self.syntax.NO_OPEN_BRACKET, self.scanner)
        
        # Get what should be a signal name in monitors
        self.symbol = self.scanner.get_symbol()

        # Skip device block, end reached (for empty block)
        if self.symbol.type == self.scanner.CLOSE_BRACKET:
            eofcheck = False
            print("Devices block is empty.")
            self.symbol = self.scanner.get_symbol()
            return

        # Read the signal name and adds it to monitors_to_add if valid
        read_signal_success = self.read_signal("monitors")
        if not read_signal_success:
            # End of file
            return True

        while self.symbol.type == self.scanner.COMMA:
            # Get next name
            self.symbol = self.scanner.get_symbol()
            print("Symbol in monitors:", self.names.get_name_string(self.symbol.id))
            read_signal_success = self.read_signal("monitors")
            # Do not need to get next symbol after name in this function loop - this is done in read_signal
        
        # Next symbol now no longer a comma. It should be a semicolon.
        if self.symbol.type != self.scanner.SEMICOLON:
            self.syntax.printerror(self.syntax.NO_SEMICOLON, self.scanner)
            return True

        print("monitors to add", self.monitors_to_add)
        for signal in self.monitors_to_add:
            [id, port_id] = self.devices.get_signal_ids(signal)
            self.monitors.make_monitor(id, port_id)
            print("Successfully created monitor for {}".format(signal))

        # Get what should be close bracket
        self.symbol = self.scanner.get_symbol()

        if self.symbol.type == self.scanner.CLOSE_BRACKET:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.EOF:
                # End of file
                return True
            else:
                self.syntax.printerror(self.syntax.EXTRA_INFORMATION_AFTER_MONITORS, self.scanner)
                return True
        else:
            self.syntax.printerror(self.syntax.NO_CLOSE_BRACKET, self.scanner)
            print ("More stuff found after monitors. Perhaps the order is wrong or more than one line used. The rest will not be read by the parser.")
            return True

    def connections_sub_block(self):
        """Call and read connections block's sub blocks.
        
        Start at point where subheader name has been read. The sub blocks are headed by the name of the device to receive inputs.
        """

        # Read expected subheader - should be a device name only
        print("Entered sub block header method inside connections block")

        # Sets device to receive inputs
        self.current_subsection = self.current_name

        # Fetch next symbol after section subheading and check it's a bracket
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type != self.scanner.OPEN_BRACKET:
            # If not a bracket, skip to next character (unique handling method to this error)
            self.syntax.printerror(self.syntax.NO_OPEN_BRACKET, self.scanner)
            return False

        # Open bracket found
        self.bracket_count = 1
        self.has_missed_bracket = False
        print("Checked for open bracket for subsection inside connections.")

        # Get first symbol of first line
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.EOF:
            eofcheck = True
            return eofcheck
        # Skip device block, end reached
        if self.symbol.type == self.scanner.CLOSE_BRACKET:
            eofcheck = False
            print("Connections sub-block is empty.")
            self.symbol = self.scanner.get_symbol()
            return eofcheck

        # Move to connection definition method
        # This recursively reads each connection line until a close bracket is found
        while (self.bracket_count%2) == 1:

            print("In method connections_sub_block, reading device name inside {} subsection in connections".format(self.current_subsection))

            if self.symbol.type == self.scanner.CLOSE_BRACKET:
                self.bracket_count += 1
                break

            # Note this method must get the symbol following every full output name
            # For gates, this is an alphanumeric set
            # For dtype, of form f.Q or f.QBAR
            read_name_success = self.read_signal("connections")
            if self.has_missed_bracket == True:
                return True

            if read_name_success == True:
                self.connection_definition(self.current_subsection, self.object_dict[self.current_subsection])
            elif read_name_success == False:
                pass
            elif self.has_missed_bracket == True:
                return True # End of file - stop parsing

            # Get first symbol of each line
            self.symbol = self.scanner.get_symbol()

        # If connection_definition tells us we have missed a bracket, recursively call the sub-block function again
        if self.has_missed_bracket == True:
            return True # End of file - stop parsing

        # Read first symbol of next line
        self.symbol = self.scanner.get_symbol()

#===========================================================================================================
#===========================================================================================================

    def skip_block(self, block):
        """Skip entire block and ends up at header of next block, by repeatedly calling skip_line() from the Scanner class.

        Method used for subheader name errors inside connections block, because it is not possible to know what is supposed to be inside a block if the header is poorly named. Start when cursor is on a bad header name. Finish after having read the first symbol of the next block (header).
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
    
    def skip_subheading_block(self):
        """Skip entire block and ends up at header of next block, by repeatedly calling skip_line() from the Scanner class.

        Method used for subheader name errors inside connections block, because it is not possible to know what is supposed to be inside a block if the header is poorly named. Start when cursor is on a bad header name. Finish after having read the first symbol of the next block (header).
        """

        while (self.symbol.type != self.scanner.CLOSE_BRACKET):
            self.scanner.skip_line()
            self.symbol = self.scanner.get_symbol()
        # Read first symbol on next line
        self.symbol = self.scanner.get_symbol()
        return     

#===========================================================================================================
#===========================================================================================================

    def connection_definition(self, subsection, device_type):
        """Parse one line of connection definition for a gate subsection.

        Used inside connections block for defining inputs. Called by read_signal() only.
        It should be read at the point after we have obtained the keyword following the output name on each line, and finish with the scanner cursor on but without having read the first symbol of the next line.

        Parameters
        -------

        'currentname': Most recent name read from calling read_name() inside the devices block.
        'device_type': The type of the device which is receiving an input.
        """

        print("Entered connection definition block")
        self.current_subsection = subsection
        
        if self.symbol.id == self.scanner.to_id:
            # Found 'to', get next symbol (expected input device name)
            self.symbol = self.scanner.get_symbol()
            if device_type != "DTYPE":
                # Call method to parse gate input name - checks if the device name matches the subsection header and has a valid port name
                self.gate_input_name(self.current_subsection)
                if self.connected == self.network.NO_ERROR:
                    # Get semicolon
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.type != self.scanner.SEMICOLON:
                        self.syntax.printerror(self.syntax.NO_SEMICOLON, self.scanner)
                        return         
                else:
                    return
            elif device_type == "DTYPE":
                # Call method to parse dtype input name - checks if the device name matches the subsection header and has a valid port name
                self.dtype_input_name(self.current_subsection)
                if self.connected == self.network.NO_ERROR:
                    # Get semicolon
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.type != self.scanner.SEMICOLON:
                        self.syntax.printerror(self.syntax.NO_SEMICOLON, self.scanner)
                        return 
            else:
                print("Something funny has happened in connection_definition")
                return

        elif self.symbol.id == self.scanner.is_id:
            # Get symbol after 'is' word. Expect 'connected'.
            self.symbol = self.scanner.get_symbol()
            if self.symbol.id == self.scanner.connected_id:
                # Found 'connected', get next symbol and check that it's 'to'
                self.symbol = self.scanner.get_symbol()
                if self.symbol.id == self.scanner.to_id:
                    # Found 'to', get what should be the same name as the block
                    self.symbol = self.scanner.get_symbol()
                    if device_type != "DTYPE":
                        self.gate_input_name(self.current_subsection)
                        # Get semicolon
                        self.symbol = self.scanner.get_symbol()
                        if self.symbol.type != self.scanner.SEMICOLON:
                            self.syntax.printerror(self.syntax.NO_SEMICOLON, self.scanner)
                            return 
                    elif device_type == "DTYPE":
                        self.dtype_input_name(self.current_subsection)
                        self.symbol = self.scanner.get_symbol()
                        if self.symbol.type != self.scanner.SEMICOLON:
                            self.syntax.printerror(self.syntax.NO_SEMICOLON, self.scanner)
                            return 
                else:
                    self.syntax.printerror(self.syntax.NO_CONNECTION_KEYWORD, self.scanner, "to")
                    return
            else: 
                self.syntax.printerror(self.syntax.NO_CONNECTION_KEYWORD, self.scanner, "connected")
                return
        else:
            self.syntax.printerror(self.syntax.NO_CONNECTION_KEYWORD, self.scanner, "to or is")
            return

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

        self.symbol = self.scanner.get_symbol()

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
                    if self.object_dict[device] == "DTYPE":
                        print("Attempting to make dtype device")
                        self.devices.make_device(self.names.query(device), self.device_kind_dict[self.object_dict[device]])

                self.symbol = self.scanner.get_symbol()

                if self.symbol == self.scanner.EOF:
                    return True

                if self.symbol.type != self.scanner.SEMICOLON:
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
        devices_to_add = [currentname]

        self.symbol = self.scanner.get_symbol()

        if self.symbol.type == self.scanner.EOF:
            return True

        while self.symbol.type == self.scanner.COMMA:
            # If comma, expect a device name afterwards
            # Fetch next thing after comma
            self.symbol = self.scanner.get_symbol()

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

            # Get next symbol
            self.symbol = self.scanner.get_symbol()

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

                self.symbol = self.scanner.get_symbol()

                if self.symbol == self.scanner.EOF:
                    return True

                if self.symbol.type != self.scanner.SEMICOLON:
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
        devices_to_add = [currentname]

        self.symbol = self.scanner.get_symbol()

        if self.symbol.type == self.scanner.EOF:
            return True

        while self.symbol.type == self.scanner.COMMA:
            # If comma, expect a device name afterwards
            # Fetch next thing after comma
            self.symbol = self.scanner.get_symbol()

            # Feed into name reader
            self.read_name("devices")
            if self.is_legal_name == False:
                return False
            devices_to_add.append(self.current_name)
            if self.name_type != "clock":
                # If you mix up device types, syntax error
                self.syntax.printerror(self.syntax.INCONSISTENT_DEVICE_NAMES, self.scanner)
            # Get next symbol after device name to check if it's a comma
            self.symbol = self.scanner.get_symbol()

        # If next symbol is definition keyword:
        # Check if symbol type is keyword and symbol ID is that for definition
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id in self.definition_ids:

            # Get next symbol
            self.symbol = self.scanner.get_symbol()
            
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

                self.symbol = self.scanner.get_symbol()

                if self.symbol == self.scanner.EOF:
                    return True

                if self.symbol.type != self.scanner.SEMICOLON:
                    self.syntax.printerror(self.syntax.NO_SEMICOLON, self.scanner)
                
                return False
        
        # If next symbol is not a definition keyword, throw error        
        else:
            self.syntax.printerror(self.syntax.NO_DEFINITION_KEYWORD, self.scanner)
            return False
        return False

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

        # Get expected comma
        self.symbol = self.scanner.get_symbol()

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

            # Check if next symbol not a number
            if self.symbol.type != self.scanner.NUMBER:
                self.syntax.printerror(self.syntax.INPUT_NUMBER_ERROR, self.scanner)
                return False

            else:
                # Get number
                temp_inputs = self.symbol.id
                print(temp_inputs)
                print("Checking devices dictionary at this point", self.object_dict)

                # Fetch and check what should be 'input' or 'inputs'
                self.symbol = self.scanner.get_symbol()
                if self.symbol.id not in [self.scanner.inputs_id, self.scanner.input_id]:
                    self.syntax.printerror(self.syntax.INPUTS_KEYWORD_ERROR)
                    return False
                # If next symbol says 'input' or 'input', update the relevant attributes
                else:
                    for device in devices_to_be_initialised:
                        device_kind = self.object_dict[device]
                        print("Device:", device, ", inputs:", temp_inputs)
                        if device_kind == "XOR":
                            self.devices.make_device(self.names.query(device), self.device_kind_dict[device_kind])
                        else:
                            self.devices.make_device(self.names.query(device), self.device_kind_dict[device_kind], temp_inputs)

                    # Get expected semicolon
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol == self.scanner.EOF:
                        return True
                    if self.symbol.type != self.scanner.SEMICOLON:
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
        self.symbol = self.scanner.get_symbol()

        if self.symbol.type == self.scanner.EOF:
            return True

        while self.symbol.type == self.scanner.COMMA:
            # If comma, expect a device name afterwards
            # Fetch next thing after comma
            self.symbol = self.scanner.get_symbol()
            print("Symbol expected to be a switch name")
            self.read_name("initialise")
            if self.is_legal_name == False:
                print("Name not legal, returning")
                return
            switches_to_be_initialised.append(self.current_name)
            if self.name_type != "switch":
                # If you mix up device types, syntax error
                self.syntax.printerror(self.syntax.INCONSISTENT_DEVICE_NAMES, self.scanner)
                return False
            # Get next symbol after device name to check if it's a comma
            self.symbol = self.scanner.get_symbol()

        print("Symbol type after finishing reading switches:", self.names.get_name_string(self.symbol.id))
        # If next symbol is definition keyword:
        # Check if symbol type is keyword and symbol ID is that for definition
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id in self.definition_ids:
            
            # Get next symbol
            self.symbol = self.scanner.get_symbol()
            print("Symbol in switch initialisation expected as definition keyword:", self.names.get_name_string(self.symbol.id))
            # Check if next symbol is switch level
            if self.symbol.id not in self.switch_level:
                self.syntax.printerror(self.syntax.SWITCH_LEVEL_ERROR, self.scanner)
                return False

            else:
                # Set switch state property for object in Device class
                # String, capitalised
                for switch in switches_to_be_initialised:
                    print("Making switch inside switch initialisation")
                    # Make device: args device_id, device_kind, switch level
                    if self.symbol.id == self.scanner.HIGH_id:
                        switch_level = 1
                    elif self.symbol.id == self.scanner.LOW_id:
                        switch_level = 0
                    self.devices.make_device(self.names.query(switch), self.devices.SWITCH, switch_level)

                self.symbol = self.scanner.get_symbol()
                if self.symbol == self.scanner.EOF:
                    return True
                if self.symbol.type != self.scanner.SEMICOLON:
                    self.syntax.printerror(self.syntax.NO_SEMICOLON, self.scanner)
                    return False
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
        self.symbol = self.scanner.get_symbol()

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
                
                # Not negative number - good to add
                if self.symbol.type == self.scanner.NUMBER:
                    # Make and initialise clock device
                    print("Making clock device")
                    self.devices.make_device(self.names.query(self.current_name), self.devices.CLOCK, self.symbol.id)

                    self.symbol = self.scanner.get_symbol()
                    if self.symbol == self.scanner.EOF:
                        return True
                    if self.symbol.type != self.scanner.SEMICOLON:
                        self.syntax.printerror(self.syntax.NO_SEMICOLON, self.scanner)
                        return False
                    return False
                else:
                    self.syntax.printerror(self.syntax.NO_CYCLE_LENGTH, self.scanner)
                    return False
            else:
                self.syntax.printerror(self.syntax.NO_LENGTH_KEYWORD, self.scanner)
                return False
        # If next symbol is not a possession keyword, throw error        
        else:
            self.syntax.printerror(self.syntax.NO_CYCLE_KEYWORD, self.scanner)
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
                    return 

            # If block is connections subheading block
            if block == "connections subheading":
                # If name is legal and does not exist in list yet, throw semantic error
                if self.is_legal_name and self.current_name not in self.object_dict:
                    self.is_legal_name = False
                    self.semantic.printerror(self.semantic.NAME_FOR_CONNECTIONS_NOT_DEFINED, self.scanner, self.current_name)
                    self.skip_subheading_block()
                    return
                elif self.is_legal_name and self.name_type != "device":
                    self.is_legal_name = False
                    self.syntax.printerror(self.syntax.CONNECTION_SUBHEADER_NAME_ERROR, self.scanner)
                    return
                elif self.is_legal_name and self.current_name in self.object_dict:
                    return 
        
        # No device name found at the beginning of the line inside the device class but not reached end of block yet
        elif self.symbol.id != self.scanner.CLOSE_BRACKET and self.symbol.type != self.scanner.NAME:
            self.syntax.printerror(self.syntax.NO_DEVICE_NAME, self.scanner)
            self.is_legal_name = False
            return

    def gate_input_name(self, subsection):
        """Check if gate input name is valid. If so, use Network method to make a connection.
    
        Start when already obtained the name of the device to have an input port. This function checks if it matches the section subheader.
        Ends without obtaining next symbol.

        Parameters
        -------

        'subsection': The subsection inside 'connections' block in which this is called. This is necessary to check that the gate input name matches that of the subsection.

        Returns
        --------

        'True' or 'False': Binary variable to track if error recovery is necessary in caller method.
        """

        # Error if input gate name does not match subsection header
        if self.names.get_name_string(self.symbol.id) != subsection:
            self.semantic.printerror(self.semantic.WRONG_INPUT_GATE_NAME, self.scanner, subsection, self.names.get_name_string(self.symbol.id))
            return 

        # Set input device id
        self.input_device_id = self.symbol.id
        # Get what should be a dot
        self.symbol = self.scanner.get_symbol()
        # Check if it is a dot
        if self.symbol.type == self.scanner.DOT:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.NAME:
                # Set input device port id
                self.input_device_port_id = self.symbol.id
                port_name = self.names.get_name_string(self.symbol.id)
                if port_name[0] == "I":
                    for char in port_name[1: len(port_name)]:
                        if not char.isdigit():
                            self.syntax.printerror(self.syntax.PORT_NAME_ERROR, self.scanner)
                            return 
                    # Valid port name found. Use Network to make connection
                    self.input_device_port = self.names.get_name_string(self.symbol.id)
                    # Only make connection in case where port id and device id exist
                    if self.devices.get_signal_name(self.input_device_id, self.input_device_port_id) != None:
                        self.connected = self.network.make_connection(self.output_device_id, self.output_device_port_id, self.input_device_id, self.input_device_port_id)
                        if self.connected == self.network.NO_ERROR:
                            print("Successfully connected gate")
                        else:
                            print("Gate connection issue")
                        return 
                    elif self.devices.get_signal_name(self.input_device_id, self.input_device_port_id) == None:
                        self.semantic.printerror(self.semantic.PORT_DOES_NOT_EXIST, self.scanner)
                        return 
                else:
                    self.syntax.printerror(self.syntax.PORT_NAME_ERROR, self.scanner)
                    return 
            else:
                self.syntax.printerror(self.syntax.NO_INPUT_PORT_NAME, self.scanner)
                return 
        else:
            self.syntax.printerror(self.syntax.MISSING_DOT_INPUT, self.scanner)
            return 

    def dtype_input_name(self, subsection):
        """Check if dtype input name is valid. If so, use Network method to make a connection.
    
        Stars when name of device to have an input port has already been read and checked that it has a valid name (it is a device already saved as a DTYPE).

        Parameters
        -------

        'subsection': The subsection inside 'connections' block in which this is called. This is necessary to check that the gate input name matches that of the subsection.

        Returns
        --------

        'True' or 'False': Binary variable to track if error recovery is necessary in caller method.
        """

        # Error if input gate name does not match subsection header
        if self.names.get_name_string(self.symbol.id) != subsection:
            self.semantic.printerror(self.semantic.WRONG_INPUT_GATE_NAME, self.scanner, subsection, self.names.get_name_string(self.symbol.id))
            return

        # Set input device id
        self.input_device_id = self.symbol.id
        # Get what should be a dot
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.DOT:
            # Found dot, check for name
            self.symbol = self.scanner.get_symbol()
            # Check if next symbol after dot is dtype input
            if self.symbol.id in self.dtype_inputs:
                # Set input device port id
                self.input_device_port_id = self.symbol.id
                # Valid port name found
                self.connected = self.network.make_connection(self.output_device_id, self.output_device_port_id, self.input_device_id, self.input_device_port_id)
                if self.connected == self.network.NO_ERROR:
                    print("Dtype successfully connected with ports:", self.names.get_name_string(self.input_device_port_id), "for device ", "and input ", self.names.get_name_string(self.output_device_id), self.names.get_name_string(self.input_device_id))
                else:
                    print("Issue with dtype connection")        
            else:
                self.syntax.printerror(self.syntax.PORT_NAME_ERROR, self.scanner)
                return
        else:
            self.syntax.printerror(self.syntax.MISSING_DOT_INPUT, self.scanner)
            return

    def read_signal(self, block):
        """Read the name of signal (output) by calling on read_name. 
        
        Start at the point where first symbol of each line has already been obtained from the scanner and return True if it is a valid output name and False otherwise. If the device name is legit, return the next symbol after the output device name. Append the signal name to list in parser __init__ method and sets the output device id and port id (for dtype only). If device type is gate, then port id = None. Sets the input device id and port id (if the input is a DTYPE output only, corresponding to Q or QBAR in Names; otherwise None).
        
        Also deal with error recovery for case in connection block where subsection close bracket in previous subsection has been missed. 

        Parameters:
        -------

        'block': name of the block in which this function is called. This is either 'connections' or 'monitors'. This determines whether an error is returned - connections is allowed to include signal names that have not yet been created, but monitors is not.

        Returns:
        -------

        'True' or 'False': binary variable tracks whether name read has been successful.
        """

        self.read_name("connections")
        if self.is_legal_name == False:
            print("Name read is not legit")
            return False
        # Skip device block, end reached
        if self.symbol.type == self.scanner.CLOSE_BRACKET:
            print("Connections block is empty.")
            return False
        # Set output device id
        self.output_device_id = self.symbol.id
        # GET NEXT SYMBOL AFTER DEVICE NAME (if monitors section and not dtype, this is a comma)
        self.symbol = self.scanner.get_symbol()

        # Check for if a close bracket has been missed
        # If close bracket missed, parser stops parsing
        if block == "connections" and self.symbol.type == self.scanner.OPEN_BRACKET and (self.bracket_count%2) == 1:
            self.syntax.printerror(self.syntax.NO_CLOSE_BRACKET, self.scanner)
            self.has_missed_bracket = True
            return False
        
        if block == "monitors" and self.symbol.type != self.scanner.DOT:
            self.monitors_to_add.append(self.current_name)
            return True

        if self.symbol.type == self.scanner.DOT and self.object_dict[self.current_name] == "DTYPE":
            self.symbol = self.scanner.get_symbol()
            if self.symbol.id in self.dtype_outputs:
                # Set output device port id
                self.output_device_port_id = self.symbol.id
                print("set output device port id")
                signal_name = ".".join((self.names.get_name_string(self.output_device_id), self.names.get_name_string(self.output_device_port_id)))
                if block == "connections" and signal_name not in self.signal_names:
                    self.signal_names.append(signal_name)
                if block == "monitors":
                    # Add to list of monitors to add
                    self.monitors_to_add.append(signal_name)
                # Get next symbol (in case of connnections block)
                self.symbol = self.scanner.get_symbol()
                return True
            else:
                self.syntax.printerror(self.syntax.DTYPE_OUTPUT_NAME_ERROR, self.scanner)
                return False
        
        elif self.symbol.type == self.scanner.DOT and self.object_dict[self.current_name] != "DTYPE":
            self.syntax.printerror(self.syntax.DOT_UNEXPECTED, self.scanner)
            return False
        
        # If not dtype output name, then parser logic for next thing after output name passed onto connection_definition method
        elif block == "connections":
            self.output_device_port_id = None
            if self.names.get_name_string(self.output_device_id) not in self.signal_names:
                self.signal_names.append(self.names.get_name_string(self.output_device_id))
            return True

#===========================================================================================================
#===========================================================================================================

    def parse_network(self):
        """Parse the circuit definition file."""

        self.eofcheck = False
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.EOF:
            print("Syntax Error: Empty file found.")
            return False
        else:
            self.eofcheck = self.circuit_description()

        if self.eofcheck == True:
            for device in self.devices.devices_list:
                print("Device", self.names.get_name_string(device.device_id), "Inputs:", device.inputs, "Outputs:", device.outputs)
            print(self.monitors.monitors_dictionary)
            for device in self.object_dict:
                device_object = self.devices.get_device(self.names.query(device))
                if device_object.clock_half_period != None:
                    print("Half period of clock {}".format(device), device_object.clock_half_period)
            self.scanner.file.close()

        self.total_errors = self.semantic.error_code_count + self.syntax.error_code_count
        if self.total_errors != 0:
            print("Parser reached end of file with {} errors".format(self.total_errors))
            return False
        else:
            return True