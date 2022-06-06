
"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""
import sys


class Symbol:
    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        self.id = None
        self.line_number = None
        self.line_position = None


class Scanner:
    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.

    print_error_line(self, error_type, error_message = ""):
                    Prints the current line when the function is called, with
                    a marker ^ showing where in the line the function was
                    called (i.e, the location of error). This function accepts
                    two arguments to output the error type and error message to
                    the user. The function skips the erroneous line and sets
                    the file pointer to the next line.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        if not isinstance(path, str):
            raise TypeError("Expected path to be a string.")

        self.names = names
        self.path = path

        # Define all symbol types
        self.symbol_type_list = [self.COMMA, self.DOT, self.SEMICOLON,
                                 self.EQUALS, self.OPEN_BRACKET,
                                 self.CLOSE_BRACKET, self.KEYWORD,
                                 self.NUMBER, self.NAME, self.EOF] = range(10)

        # Define all keywords
        self.keywords_list = ["devices", "initialise", "connections",
                              "monitors", "has", "have", "is", "are", "to",
                              "connected", "input", "inputs", "cycle",
                              "length", "AND", "OR", "NOR",
                              "XOR", "NAND", "NOT", "DTYPE", "SWITCH", "CLOCK",
                              "HIGH", "LOW", "DATA", "CLK", "SET",
                              "CLEAR", "Q", "QBAR"]
        [self.devices_id, self.initialise_id, self.connections_id,
         self.monitors_id, self.has_id, self.have_id, self.is_id, self.are_id,
         self.to_id, self.connected_id, self.input_id, self.inputs_id,
         self.cycle_id, self.length_id, self.AND_id,
         self.OR_id, self.NOR_id, self.XOR_id, self.NAND_id, self.NOT_id,
         self.DTYPE_id, self.SWITCH_id, self.CLOCK_id, self.HIGH_id, self.LOW_id,
         self.DATA_id, self.CLK_id, self.SET_id, self.CLEAR_id, self.Q_id,
         self.QBAR_id] = self.names.lookup(self.keywords_list)

        self.current_character = " "
        self.current_line = 0
        self.current_character_position = -1

        try:
            file = open(path)
        except OSError:
            print("This file could not be opened, perhaps it doesn't exist")
            sys.exit()
        self.file = file
        self.lines = self.file.read().splitlines()
        self.file.seek(0)

    def advance(self):
        """Read next character from file."""
        self.current_character = self.file.read(1)
        if self.current_character == "\n":
            self.current_line += 1
            self.current_character_position = -1
        else:
            self.current_character_position += 1
        return

    def skip_spaces(self):
        """Skips until non-space character is reached."""
        while self.current_character.isspace():
            self.advance()
        return

    def skip_comment(self):
        """Skips the current comment (Until next semicolon or newline)."""
        while self.current_character not in [";", "\n", ""]:
            self.advance()
        self.advance()
        return

    def print_error_line(self, line_number, line_position, error_message=""):
        """Print current line with marker pointing where the error is."""

        print("Line {}, {}: {}".format(line_number, line_position, error_message))
        print(self.lines[line_number])
        print(" " * (line_position - 1) + "^ Error here")

    def get_name(self):
        """Read and returns the next name (word made up of only letters)."""
        name = ""
        while self.current_character.isalnum():
            name += self.current_character
            self.advance()
        return name

    def get_number(self):
        """Read and returns the next number."""
        number = ""
        while self.current_character.isdigit():
            number += self.current_character
            self.advance()
        return int(number)

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol()
        self.skip_spaces()  # Current character is now not whitespace

        symbol.line_number = self.current_line
        symbol.line_position = self.current_character_position


        if self.current_character.isalpha():  # Name
            name_string = self.get_name()
            # print(name_string) # For tests
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.NAME
            [symbol.id] = self.names.lookup([name_string])

        elif self.current_character.isdigit():  # Number
            symbol.id = self.get_number()
            # print(symbol.id) # For tests
            symbol.type = self.NUMBER

        elif self.current_character == ",":  # Punctuation
            symbol.type = self.COMMA
            self.advance()

        elif self.current_character == ".":
            symbol.type = self.DOT
            self.advance()

        elif self.current_character == ";":
            symbol.type = self.SEMICOLON
            self.advance()

        elif self.current_character == "=":
            symbol.type = self.EQUALS
            self.advance()

        elif self.current_character == "(":
            symbol.type = self.OPEN_BRACKET
            self.advance()

        elif self.current_character == ")":
            symbol.type = self.CLOSE_BRACKET
            self.advance()

        elif self.current_character == "":  # End of File
            symbol.type = self.EOF

        elif self.current_character == "#":  # Comment Check
            self.skip_comment()
            symbol = self.get_symbol()

        else:  # Not a valid character (symbol.type == None)
            self.advance()

        return symbol
