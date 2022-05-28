"""Error handling for parser to read circuit definition file.

Used in the Logic Simulator project to provide produce custom exceptions using class inheritance from built-in Exception clas, for syntactic and semantic errors.

Classes
-------
'SyntaxError': Skeleton class for syntax errors.

'OpenParentheses': Missing open bracket.

'CloseParentheses': Missing close bracket.

'LineEnd': Missing semicolon or open bracket (in case of block header)

'BlockHeader': Missing or misspelled block header.

'PossessionKeyword': Missing or misspelled possession keyword.

'DefinitionKeyword': Missing or misspelled definition keyword.

'XName': Skeleton class for gate/dtype/switch/clock illegal name errors.

'DeviceName': Missing device name.

'IllegalDeviceName': Illegal generic device name.

'IllegalGateName': Illegal gate name.

'IllegalSwitchName': Illegal switch name.

'IllegalClockName': Illegal clock name.

'IllegalInputName': Illegal input name.

'ConnectionDefinition': Missing 

'ExtraChars': Extra characters not expected in location specified.

'SemanticError': Skeleton class for semantic errors.
"""

from scanner import Scanner

class SemanticError(Exception):
    pass

class SyntaxError(Exception):

    def __init__(self, message, *args):
        """Set parameters to report error.
        
        Parameters
        -------

        'message': Output to be printed to terminal.

        """
        self.message = message
        sub_error_type = ""
        error_type = "SyntaxError: {}".format(sub_error_type)
        
        # Print error to terminal using method in Scanner class.
        # Skip line to resume parsing after the next semicolon.
        Scanner.print_error_line(error_type, self.message)

class OpenParentheses(SyntaxError):

    def __init__(self):
        super(CloseBracket, self).__init__(
            "Missing open parentheses following section or subsection heading."
        )
        sub_error_type = "Open Parantheses"

class CloseParentheses(SyntaxError):

    def __init__(self):
        super(CloseParentheses, self).__init__(
            "Missing close parentheses following section or subsection initialisation."
        )
        sub_error_type = "Close Parantheses"

class BlockHeader(SyntaxError):

    def __init__(self, section):
        if section in Scanner.keywords_list [0:4]:
            super(BlockHeader, self).__init__(
                "Missing header for section {}".format(section)
            )
        else:
            super(BlockHeader, self).__init__(
                "Missing header for subsection {}".format(section)
            )

class DeviceName(SyntaxError):

    def __init__(self, section):
        if section in Scanner.keywords_list [0:4]:
            super(DeviceName, self).__init__(
                "Missing header for section {}".format(section)
            )
        else:
            super(BlockHeader, self).__init__(
                "Missing header for subsection {}".format(section)
            )

