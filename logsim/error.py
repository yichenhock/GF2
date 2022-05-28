"""Error handling for parser to read circuit definition file.

Used in the Logic Simulator project to provide classes for unique error types, both semantic and syntactic.

Classes
-------
'SyntaxError': Skeleton class for syntax errors.

'OpenParentheses': Missing open bracket.

'CloseParentheses': Missing close bracket.

'LineEnd': Missing semicolon or open bracket (in case of block header)

'BlockHeader': Missing or misspelled block header.

'PossessionKeyword': Missing or misspelled possession keyword.

'DefinitionKeyword': Missing or misspelled definition keyword.

'XName': Skeleton class for gate/dtype/switch/clock name errors.

'DeviceName': Missing or illegal device name.

'DTypeName': Missing or illegal dtype name.

'SwitchName': Missing or illegal switch name.

'ClockName': Missing or illegal clock name.

'InputName': Missing or illegal input name.

'ConnectionDefinition': Missing 

'ExtraChars': Extra characters not expected in location specified.

'SemanticError': Skeleton class for semantic errors.
"""

from scanner import Scanner

class SemanticError():
    pass

class SyntaxError():

    def __init__(self, message):
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

class OpenParantheses(SyntaxError):

    def __init__(self):
        def super(CloseBracket, self).__init__(
            "Missing open parentheses following section or subsection heading."
        )
        sub_error_type = "Open Parantheses"

class CloseParantheses(SyntaxError):

    def __init__(self):
        def super(CloseBracket, self).__init__(
            "Missing close parentheses following section or subsection initialisation."
        )
        sub_error_type = "Close Parantheses"

class 


