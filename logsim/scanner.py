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
        self.symbol_type_list = [self.COMMA, self.DOT, self.SEMICOLON, self.EQUALS, self.BRACKETOPEN, self.BRACKETCLOSE, self.KEYWORD, self.NUMBER, self.NAME, self.EOF] = range(10)
        self.keywords_list = ["devices", "initialise", "connections", "monitors"]
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


