

class ParserError(Exception):
    """Base class for all input file processing errors."""
    def __init__(self, symbol, message): 
        """Initialise error and its message."""
        self.symbol = symbol 
        self.message = message 
    
    def __eq__(self, error2): 
        """Check if one error is the same as another error."""
        is_equal = False 
        if self.symbol == error2.symbol and self.message == error2.message and type(self) == type(error2):
            is_equal = True
        return is_equal

class ParserSemanticError(ParserError): 
    """Base class for all semantic errors."""
    pass 

class ParserSyntaxError(ParserError): 
    """Base class for all syntax errors."""
    pass 

# Semantic errors

class UndefinedError(ParserSemanticError):
    def __init__(self, symbol, name): 
        message = "Device {} must be defined before use.".format(name)
        super().__init__(symbol, message)

class RedefinedError(ParserSemanticError):
    def __init__(self, symbol, name): 
        message = "Device {} has been previously defined.".format(name)
        super().__init__(symbol, message)

# Syntax errors

class BlockError(ParserSyntaxError): 
    def __init__(self, symbol): 
        message = "Expected a block header (either 'devices', 'initialise', 'connections' or 'monitor')"
        super().__init__(symbol, message)

class SemicolonError(ParserSyntaxError):
    def __init__(self, symbol): 
        message = "Expected a ';'"
        super().__init__(symbol, message)

class OpenBracketError(ParserSyntaxError):
    def __init__(self, symbol): 
        message = "Expected a '('"
        super().__init__(symbol, message)

class CloseBracketError(ParserSyntaxError):
    def __init__(self, symbol): 
        message = "Expected a ')'"
        super().__init__(symbol, message)

class InvalidDeviceRule(ParserSyntaxError):
    def __init__(self, symbol): 
        message = "Invalid device statement (expected ',' or 'is'/'are')."
        super().__init__(symbol, message)

class DeviceTypeError(ParserSyntaxError):
    def __init__(self, symbol): 
        message = "Expected a device type."
        super().__init__(symbol, message)

class InvalidDeviceName(ParserSyntaxError):
    def __init__(self, symbol): 
        message = "Expected a device name."
        super().__init__(symbol, message)

class WrongDeviceName(ParserSyntaxError):
    def __init__(self, symbol, name): 
        message = "Device name should not be {} (must not begin with 'sw' or 'clk').".format(name)
        super().__init__(symbol, message)

class WrongSwitchName(ParserSyntaxError):
    def __init__(self, symbol, name): 
        message = "Switch name should not be {} (must begin with 'sw' followed by a number).".format(name)
        super().__init__(symbol, message)
        
class WrongClockName(ParserSyntaxError):
    def __init__(self, symbol, name): 
        message = "Clock name should not be {} (must begin with 'clk' followed by a number).".format(name)
        super().__init__(symbol, message)