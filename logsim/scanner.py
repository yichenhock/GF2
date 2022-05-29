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
                    the user. The function skips the erroneous line and sets the
                    file pointer to the next line.
    """
    
    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""

        self.names = names

        #Define all symbol types
        self.symbol_type_list = [self.COMMA, self.DOT, self.SEMICOLON, self.EQUALS, self.BRACKET_OPEN, self.BRACKET_CLOSE, self.HASH, self.NAME, self.KEYWORD, self.NUMBER, self.EOF] = range(11)

        #Define all keywords
        self.keywords_list = ["devices", "initialise", "connections", "monitors", "has", "have", "is", "are", "to", "connected", "input", "inputs", "cycle", "length", "AND", "OR", "NOR", "XOR", "NAND", "DTYPE",  "SWITCH", "CLOCK", "HIGH", "LOW", "DATA", "CLK", "SET", "CLEAR", "Q", "QBAR"]
        [self.devices_id, self.initialise_id, self.connections_id, self.monitors_id, self.has_id, self.have_id, self.is_id, self.are_id, self.to_id, self.connected_id, self.input_id, self.inputs_id, self.cycle_id, self.length_id, self.AND_id, self.OR_id, self.NOR_id, self.XOR_id, self.NAND_id, self.DTYPE_id, self.SWITCH_id, self.CLOCK_id, self.HIGH_id, self.LOW_id, self.DATA_id, self.CLK_id, self.SET_id, self.CLEAR_id, self.Q_id, self.QBAR_id] = self.names.lookup(self.keywords_list)

        self.current_character = " "
        self.current_line = 0
        self.current_character_position = -1


        try: 
            file = open(path)
        except OSError: 
            print("This file could not be opened, perhaps it doesn't exist")
            sys.exit()
        self.file = file
        self.lines = self.file.readlines()
        self.file.seek(0)

    def advance(self): #Reads next character from file
        self.current_character = self.file.read(1)
        if self.current_character == "\n":
            self.current_line += 1
            self.current_character_position = -1
        else:
            self.current_character_position += 1
        return

    def skip_spaces(self): #Skips until non-space character is reached
        while self.current_character.isspace():
            self.advance()
        return

    def skip_line(self): #Skips until next semicolon or bracket
        while self.current_character not in [";", "(", ")"]:
            self.advance()
        self.advance()
        return

    @staticmethod
    def print_error_line(self, error_type, error_message = ""): #See comments at top of Scanner class
        print("Error type:", error_type)
        print(self.lines[self.current_line], end = "")
        print(" " * (self.current_character_position - 1), "^ Error Here")
        print(error_message)
        self.skip_line()

    def get_name(self): #Reads and returns the next name (alphanumeric word)
        name = ""
        while self.current_character.isalnum():
            name += self.current_character
            self.advance()
        return name

    def get_number(self): #Reads and returns the next number
        number = ""
        while self.current_character.isdigit():
            number += self.current_character
            self.advance()
        return int(number)

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol()
        self.skip_spaces() #Current character is now not whitespace
            
        #print(self.current_character)

        if self.current_character == "#":
            symbol.type = self.HASH
            self.skip_line()

        elif self.current_character.isalpha(): #Name
            name_string = self.get_name()
            print(name_string)
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.NAME
            [symbol.id] = self.names.lookup([name_string])

        elif self.current_character.isdigit(): #Number
            symbol.id = self.get_number()
            print(symbol.id)
            symbol.type = self.NUMBER

        elif self.current_character == ",": #Punctuation
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
            symbol.type = self.BRACKET_OPEN
            self.advance()

        elif self.current_character == ")": 
            symbol.type = self.BRACKET_CLOSE
            self.advance()

        elif self.current_character == "": #End of File
            symbol.type = self.EOF
        
        else: #Not a valid character
            # print("Not a valid character")
            self.print_error_line("Undefined Character", "Not a valid character")
            self.advance()

        return symbol