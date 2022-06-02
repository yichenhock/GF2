"""Error handling for parser to read circuit definition file.

Used in the Logic Simulator project to provide produce custom exceptions using class inheritance from built-in Exception clas, for syntactic and semantic errors.

Classes
-------
'SyntaxError': Class for syntax errors. 

'SemanticError': Class for semantic errors.
"""
from scanner import Scanner

class SemanticError():

    def __init__(self):
        """Set parameters to report error."""

        self.id_list = [self.WRONG_GATE_FOR_NAME, self.NAME_ALREADY_EXISTS, self.NAME_FOR_INITIALISE_NOT_DEFINED, self.NAME_FOR_CONNECTIONS_NOT_DEFINED, self.WRONG_INPUT_GATE_NAME, self.NAME_FOR_MONITORS_NOT_DEFINED, self.SIGNAL_ALREADY_EXISTS, self.PORT_DOES_NOT_EXIST] = range(8)

        self.error_type_list = ["WRONG_GATE_FOR_NAME", "NAME_ALREADY_EXISTS", "NAME_FOR_INITIALISE_NOT_DEFINED", "NAME_FOR_CONNECTIONS_NOT_DEFINED", "WRONG_INPUT_GATE_NAME", "NAME_FOR_MONITORS_NOT_DEFINED", "SIGNAL_ALREADY_EXISTS", "PORT_DOES_NOT_EXIST"]

        self.error_code_count = 0

    def printerror(self, id, scanner, symbol1=None, symbol2=None):
        """Print error message to terminal and skip line.
        
        Parameters
        -------

        'message': Output to be printed to terminal.
        """
        
        self.scanner = scanner

        self.message_list = ["Wrong gate type provided for device name chosen. Given {}, expected {}".format(symbol1, symbol2),
        "Device name {} defined has already been used above.".format(symbol1), 
        "The device name {} provided in the initialisation section has not been defined in the devices section.".format(symbol1), 
        "The device name {} provided in the connections section has not been defined in the devices section.".format(symbol1), 
        "Wrong input gate name for connection section subheader. The subheader name should be the name of the device receiving inputs. Expected {}, got {}.".format(symbol1, symbol2), 
        "The device name {} provided in the monitors section has not been defined in the devices section.".format(symbol1), 
        "The signal name defined in connections section already exists.", "The input port specified does not exist."]

        self.message = "ParserSemanticError: {}".format(self.message_list[id])
        
        # Print error to terminal using method in Scanner class.
        # Skip line to resume parsing after the next semicolon.
        self.scanner.print_error_line(self.error_type_list[id], self.message)
        self.error_code_count += 1
        
class SyntaxError():

    def __init__(self):
        """Set parameters to report error."""

        self.id_list = [self.NO_OPEN_BRACKET, self.NO_CLOSE_BRACKET, self.DEVICE_LETTER_CAPITAL, self.NO_DEVICE_NAME, self.NO_HEADER, self.HEADER_NAME_ERROR, self.NO_DEFINITION_KEYWORD, self.NO_POSSESSION_KEYWORD, self.DEVICE_TYPE_ERROR, self.INCORRECT_SWITCH_NAME, self.INCORRECT_CLOCK_NAME, self.NO_SEMICOLON, self.INCONSISTENT_DEVICE_NAMES, self.MISSING_SECTION,

        self.INPUT_NUMBER_ERROR, self.INPUTS_KEYWORD_ERROR, self.SWITCH_LEVEL_ERROR, self.NO_CYCLE_KEYWORD, self.NO_LENGTH_KEYWORD, self.NO_CYCLE_LENGTH,

        self.NO_CONNECTION_KEYWORD, self.NO_INPUT_GATE_NAME, self.NO_INPUT_PORT_NAME, self.MISSING_DOT_INPUT, self.PORT_NAME_ERROR, self.CONNECTION_SUBHEADER_NAME_ERROR, self.DTYPE_OUTPUT_NAME_ERROR, self.DOT_UNEXPECTED,

        self.NO_MONITOR_NAME, self.EXTRA_INFORMATION_AFTER_MONITORS, self.EMPTY_FILE] = range(31)

        self.error_type_list = ["NO_OPEN_BRACKET", "NO_CLOSE_BRACKET", "DEVICE_LETTER_CAPITAL", "NO_DEVICE_NAME", "NO_HEADER", "HEADER_NAME_ERROR", "NO_DEFINITION_KEYWORD", "NO_POSSESSION_KEYWORD", "DEVICE_TYPE_ERROR", "INCORRECT_SWITCH_NAME", "INCORRECT_CLOCK_NAME", "NO_SEMICOLON", "INCONSISTENT_DEVICE_NAMES", "MISSING_SECTION",

        "INPUT_NUMBER_ERROR", "INPUTS_KEYWORD_ERROR", "SWITCH_LEVEL_ERROR", "NO_CYCLE_KEYWORD", "NO_LENGTH_KEYWORD", "NO_CYCLE_LENGTH", 

        "NO_CONNECTION_KEYWORD", "NO_INPUT_GATE_NAME", "NO_INPUT_PORT_NAME", "MISSING_DOT_INPUT", 
        "PORT_NAME_ERROR", "CONNECTION_SUBHEADER_NAME_ERROR", "DTYPE_OUTPUT_NAME_ERROR", "DOT_UNEXPECTED",

        "NO_MONITOR_NAME", "EXTRA_INFORMATION_AFTER_MONITORS", "EMPTY_FILE"]

        self.error_code_count = 0

    def printerror(self, id, scanner, symbol1=None):
        """Print error message to terminal and skip line.
        
        Parameters
        -------

        'message': Output to be printed to terminal.
        """

        self.scanner = scanner
        
        self.message_list = ["Missing open parentheses following section header. Parser will skip next line of code. Please fix and rerun.", 
        "Missing close parentheses following section or subsection initialisation.", 
        "Device names must not contain capitalised letters.", 
        "Device, switch or clock name missing. Please provide a valid alphanumeric name.", 
        "Section header missing", 
        "Section header name {} is not legal.".format(symbol1), 
        "Missing definition keyword.", 
        "Missing possession keyword.", 
        "Device type is not legal.", 
        "'sw' must be followed by a number only. 'sw' at the start of a name is a reserved device naming keyword indicating a switch.", 
        "'clk' must be followed by a number only. 'clk' at the start of a name is a reserved device naming keyword indicating a clock.", 
        "Semicolon expected at line end, but none found.", 
        "Inconsistent device name types on each line. Switches, clocks and devices must be grouped separately.", 
        "Section {} missing where expected.".format(symbol1), 
        
        "Input number missing where expected.", 
        "Initialisation line for devices should end in keyword 'input' or 'inputs'.", 
        "Switch level may only be HIGH or LOW.", 
        "Keyword 'cycle' missing from clock cycle length definition.", 
        "Keyword 'length' missing from clock cycle length definition.", 
        "Cycle length (number) missing from clock cycle length definition.", 

        "Connection keyword missing. Check that connections are made using the phrases 'is connected to' or 'to' only. Expected {}.".format(symbol1), 
        "No input gate name given in connection section. Check that a valid gate has been specified.", 
        "Missing input port name. Check that a valid name is used - of form 'IN' followed by a number.", 
        "Missing dot in input name. Names should be of form e.g. 'a.I1'.", 
        "Port names need to be of form 'IN' followed by a number.", 
        "Subheaders are devices to receive inputs. These cannot be switches or clocks.", 
        "No correct dtype output port name given where expected. This should be Q or QBAR.", 
        "Unexpected dot following name of none dtype used to define name of output. Only dtype outputs should take this form, e.g.: a.Q, a.QBAR.",

        "Missing name in monitor section.", 
        "Extra information provided in circuit definition file after end of the monitors block. Please ensure that this is moved elsewhere if it is important as it will not be read.", "Circuit definition text file is either empty or does not contain characters recognised by the scanner."]

        self.message = "ParserSyntaxError: {}".format(self.message_list[id])
        
        # Print error
        # Do not skip line
        if id == self.NO_CLOSE_BRACKET:
            print("Error type: NO_CLOSE_BRACKET")
            print(self.scanner.lines[self.scanner.current_line])
            print("^ Error before this line")
            print(self.message)
            self.error_code_count += 1
            
        # Print error to terminal using method in Scanner class.
        # Skip line to resume parsing after the next semicolon.
        else:
            self.scanner.print_error_line(self.error_type_list[id], self.message)
            self.error_code_count += 1