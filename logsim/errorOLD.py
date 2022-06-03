"""Error handling for parser to read circuit definition file.

Used in the Logic Simulator project to provide produce custom exceptions using class inheritance from built-in Exception clas, for syntactic and semantic errors.

Classes
-------
'SyntaxError': Class for syntax errors. 

'SemanticError': Class for semantic errors.
"""
from scanner import Scanner


class SemanticError():
    """Handle semantic errors in circuit definition file.
    
    Parameters
    ----------
    id: error id from error id list.
    """

    def __init__(self):
        """Set parameters to report error."""
        self.id_list = [self.WRONG_GATE_FOR_NAME, self.NAME_ALREADY_EXISTS, self.NAME_FOR_INITIALISE_NOT_DEFINED, self.NAME_FOR_CONNECTIONS_NOT_DEFINED, self.WRONG_INPUT_GATE_NAME,
                        self.NAME_FOR_MONITORS_NOT_DEFINED, self.PORT_DOES_NOT_EXIST, self.TOO_MANY_INPUTS, self.EMPTY_INPUTS, self.KEYWORD_AS_NAME, self.DEVICE_NOT_INITIALISED] = range(11)

        self.error_type_list = ["WRONG GATE FOR NAME", "NAME ALREADY EXISTS", "NAME FOR INITIALISE NOT DEFINED", "NAME FOR CONNECTIONS NOT DEFINED",
                                "WRONG INPUT GATE NAME", "NAME FOR MONITORS NOT DEFINED", "PORT DOES NOT EXIST", "TOO MANY INPUTS", "EMPTY INPUTS", "KEYWORD AS NAME", "DEVICE NOT INITIALISED"]

        self.error_code_count = 0

        self.array_of_errors = []

    def printerror(self, id, scanner, symbol1=None, symbol2=None):
        """Print error message to terminal and skip line.

        Parameters
        -------
        'message': Output to be printed to terminal.
        """
        self.scanner = scanner

        self.message_list = ["Wrong gate type provided for device name chosen. Given {}, expected {}".format(symbol1, symbol2),
                             "Device name {} defined has already been used above.".format(
                                 symbol1),
                             "The device name {} provided in the initialisation section has not been defined in the devices section.".format(
                                 symbol1),
                             "The device name {} provided in the connections section has not been defined in the devices section.".format(
                                 symbol1),
                             "Wrong input gate name for connection section subheader. The subheader name should be the name of the device receiving inputs. Expected {}, got {}.".format(
                                 symbol1, symbol2),
                             "The device name {} provided in the monitors section has not been defined in the devices section.".format(symbol1), "The input port specified does not exist.", "Too many inputs have been defined for the gate specified.", "Some input gates to device have not been connected to any signal.", "Reserved keyword in place of device name. Please observe the list of keywords.", "A gate, dtype, switch or clock defined in the devices section has not been initialised."]

        self.message = "Parser Semantic Error: {}".format(
            self.message_list[id])

        if id == self.EMPTY_INPUTS:
            print("Error type: EMPTY INPUTS")
            print(self.scanner.lines[self.scanner.current_line-2])
            print("^ Error after this line")
            print(self.message)
            self.error_code_count += 1
            self.array_of_errors.append(self.EMPTY_INPUTS)

        else:
            # Print error to terminal using method in Scanner class.
            # Skip line to resume parsing after the next semicolon.
            self.scanner.print_error_line(
                self.error_type_list[id], self.message)
            self.array_of_errors.append(id)
            self.error_code_count += 1


class SyntaxError():

    def __init__(self):
        """Set parameters to report error."""
        self.id_list = [self.NO_OPEN_BRACKET, self.NO_CLOSE_BRACKET, self.DEVICE_LETTER_CAPITAL, self.NO_DEVICE_NAME, self.NO_HEADER, self.HEADER_NAME_ERROR, self.NO_DEFINITION_KEYWORD, self.NO_POSSESSION_KEYWORD, self.DEVICE_TYPE_ERROR, self.INCORRECT_SWITCH_NAME, self.INCORRECT_CLOCK_NAME, self.NO_SEMICOLON, self.INCONSISTENT_DEVICE_NAMES, self.MISSING_SECTION,

                        self.INPUT_NUMBER_ERROR, self.INPUTS_KEYWORD_ERROR, self.SWITCH_LEVEL_ERROR, self.NO_CYCLE_KEYWORD, self.NO_LENGTH_KEYWORD, self.NO_CYCLE_LENGTH,

                        self.NO_CONNECTION_KEYWORD, self.NO_INPUT_GATE_NAME, self.NO_INPUT_PORT_NAME, self.MISSING_DOT_INPUT, self.PORT_NAME_ERROR, self.CONNECTION_SUBHEADER_NAME_ERROR, self.DTYPE_OUTPUT_NAME_ERROR, self.DOT_UNEXPECTED,

                        self.NO_MONITOR_NAME, self.EXTRA_INFORMATION_AFTER_MONITORS] = range(30)

        self.error_type_list = ["NO OPEN BRACKET", "NO CLOSE BRACKET", "DEVICE LETTER_CAPITAL", "NO DEVICE NAME", "NO HEADER", "HEADER NAME ERROR", "NO DEFINITION KEYWORD", "NO POSSESSION KEYWORD", "DEVICE TYPE ERROR", "INCORRECT SWITCH NAME", "INCORRECT CLOCK NAME", "NO SEMICOLON", "INCONSISTENT DEVICE NAMES", "MISSING SECTION",

                                "INPUT NUMBER ERROR", "INPUTS KEYWORD ERROR", "SWITCH LEVEL ERROR", "NO CYCLE KEYWORD", "NO LENGTH KEYWORD", "NO CYCLE LENGTH",

                                "NO CONNECTION KEYWORD", "NO INPUT GATE NAME", "NO INPUT PORT NAME", "MISSING DOT INPUT",
                                "PORT NAME ERROR", "CONNECTION SUBHEADER NAME ERROR", "DTYPE OUTPUT NAME ERROR", "DOT UNEXPECTED",

                                "NO MONITOR NAME", "EXTRA INFORMATION AFTER MONITORS"]

        self.error_code_count = 0

        self.array_of_errors = []

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
                             "Section header name {} is not legal.".format(
                                 symbol1),
                             "Missing definition keyword.",
                             "Missing possession keyword.",
                             "Device type is not legal.",
                             "'sw' must be followed by a number only. 'sw' at the start of a name is a reserved device naming keyword indicating a switch.",
                             "'clk' must be followed by a number only. 'clk' at the start of a name is a reserved device naming keyword indicating a clock.",
                             "Semicolon expected at line end, but none found.",
                             "Inconsistent device name types on each line. Switches, clocks and devices must be grouped separately.",
                             "Section {} missing where expected.".format(
                                 symbol1),

                             "Input number missing where expected.",
                             "Initialisation line for devices should end in keyword 'input' or 'inputs'.",
                             "Switch level may only be HIGH or LOW.",
                             "Keyword 'cycle' missing from clock cycle length definition.",
                             "Keyword 'length' missing from clock cycle length definition.",
                             "Cycle length (number) missing from clock cycle length definition.",

                             "Connection keyword missing. Check that connections are made using the phrases 'is connected to' or 'to' only. Expected {}.".format(
                                 symbol1),
                             "No input gate name given in connection section. Check that a valid gate has been specified.",
                             "Missing input port name. Check that a valid name is used - of form 'IN' followed by a number.",
                             "Missing dot in input name. Names should be of form e.g. 'a.I1'.",
                             "Port names need to be of form 'IN' followed by a number.",
                             "Subheaders are devices to receive inputs. These cannot be switches or clocks.",
                             "No correct dtype output port name given where expected. This should be Q or QBAR.",
                             "Unexpected dot following name of none dtype used to define name of output. Only dtype outputs should take this form, e.g.: a.Q, a.QBAR.",

                             "Missing name in monitor section.",
                             "Extra information provided in circuit definition file after end of the monitors block. Please ensure that this is moved elsewhere if it is important as it will not be read."]

        self.message = "Parser Syntax Error: {}".format(self.message_list[id])

        # Print error
        # Do not skip line
        if id == self.NO_CLOSE_BRACKET:
            print("Error type: NO CLOSE BRACKET")
            print(self.scanner.lines[self.scanner.current_line])
            print("^ Error before this line")
            print(self.message)
            self.error_code_count += 1
            self.array_of_errors.append(self.NO_CLOSE_BRACKET)

        # Print error to terminal using method in Scanner class.
        # Skip line to resume parsing after the next semicolon.
        else:
            self.scanner.print_error_line(
                self.error_type_list[id], self.message)
            self.array_of_errors.append(id)
            self.error_code_count += 1
