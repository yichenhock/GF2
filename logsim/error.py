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

class SemanticError():
    pass

class SyntaxError():

    def __init__(self):
        """Set parameters to report error.
        
        Parameters
        -------

        'message': Output to be printed to terminal.

        """

        self.id_list = [self.NO_CLOSE_BRACKET, self.DEVICE_LETTER_CAPITAL, self.DEVICE_TYPE_ERROR, self.DEVICE_NAME_MISSING, self.HEADER_NAME_ERROR] = range(len(self.id_list))

        self.error_type_list = ["NO_CLOSE_BRACKET", "DEVICE_LETTER_CAPITAL", "DEVICE_TYPE_ERROR", "NO_DEVICE_NAME", "NO_DEVICE_BLOCK", "NO_HEADER", "HEADER_NAME_ERROR"]

        self.message_list = ["Missing close parentheses following section or subsection initialisation.", "Device names must not contain capitalised letters.", "Device name missing. Please provide a valid alphanumeric device name.", "Device block missing. Please provide at least one device inside the device block and a block header.", "Section header missing"]

    def print(self, id, symbol=None):

        self.message = "SyntaxError: {}".format(self.message_list(id))
        
        # Print error to terminal using method in Scanner class.
        # Skip line to resume parsing after the next semicolon.
        Scanner.print_error_line(self.error_type_list(id), self.message)
    


# class OpenParentheses(SyntaxError):

#     def __init__(self):
#         super(OpenParentheses, self).__init__(
#             "Missing open parentheses following section or subsection heading."
#         )
#         sub_error_type = "Open Parantheses"

# class CloseParentheses(SyntaxError):

#     def __init__(self):
#         super(CloseParentheses, self).__init__(
#             "Missing close parentheses following section or subsection initialisation."
#         )
#         sub_error_type = "Close Parantheses"

# class BlockHeader(SyntaxError):

#     def __init__(self, section):
#         if section in Scanner.keywords_list [0:4]:
#             super(BlockHeader, self).__init__(
#                 "Missing header for section {}".format(section)
#             )
#         else:
#             super(BlockHeader, self).__init__(
#                 "Missing header for subsection {}".format(section)
#             )

# class DeviceName(SyntaxError):

#     def __init__(self, section):
#             super(DeviceName, self).__init__(
#                 "Missing header for subsection {}".format(section)
#             )

