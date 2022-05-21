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
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""

        self.names = names
        self.symbol_type_list = [self.COMMA, self.DOT, self.SEMICOLON, self.EQUALS, self.BRACKET_OPEN, self.BRACKET_CLOSE, self.KEYWORD, self.NUMBER, self.NAME, self.EOF] = range(10)
        self.keywords_list = ["devices", "initialise", "connections", "monitors", "has", "have", "is", "are"]
        [self.devices_id, self.initialise_id, self.connections_id, self.monitors_id] = self.names.lookup(self.keywords_list)
        self.current_character = ""

        try: 
            file = open(path)
        except OSError: 
            print("This file could not be opened, perhaps it doesn't exist")
            sys.exit()
        self.file = file

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""

        symbol = Symbol()
        self.skip_spaces() #Current character is now not whitespace

        if self.current_character.isalpha(): #Name
            name_string = self.get_name()
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.NAME
            [symbol.id] = self.names.lookup([name_string])

        elif self.current_character.isdigit(): #Number
            symbol.id = self.get_number()
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

        elif self.current_character == "": #End of File
            symbol.type = self.EOF
        
        else: #Not a valid character
            self.advance()

        return symbol

#sort out keywords
#make functions used in get_symbol (eg, get_name)