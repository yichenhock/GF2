

class ParserError(Exception):
    """Base class for all input file processing errors."""

    def __init__(self, symbol, message):
        """Initialise error and its message."""
        self.symbol = symbol
        self.message = message

    def __eq__(self, error2):
        """Check if one error is the same as another error."""
        is_equal = False
        if self.symbol == error2.symbol and self.message == error2.message \
                and type(self) == type(error2):
            is_equal = True
        return is_equal


class ParserSemanticError(ParserError):
    """Base class for all semantic errors."""
    pass


class ParserSyntaxError(ParserError):
    """Base class for all syntax errors."""
    pass

# =============================================================================
# =============================================================================

# Semantic errors


class UndefinedError(ParserSemanticError):
    def __init__(self, symbol, name):
        message = "Device '{}' must be defined before use.".format(name)
        super().__init__(symbol, message)


class RedefinedError(ParserSemanticError):
    def __init__(self, symbol, name):
        message = "Device '{}' has been previously defined.".format(name)
        super().__init__(symbol, message)


class WrongDeviceName(ParserSemanticError):
    def __init__(self, symbol, name):
        message = "Device name should not be '{}' (must not begin with 'sw' or 'clk').".format(
            name)
        super().__init__(symbol, message)


class InvalidClockLength(ParserSemanticError):
    def __init__(self, symbol):
        message = "Clock length needs to be an integer between 1 and 1000."
        super().__init__(symbol, message)


class WrongSwitchName(ParserSemanticError):
    def __init__(self, symbol, name):
        message = "Switch name should not be '{}' (must begin with 'sw' followed by a number).".format(
            name)
        super().__init__(symbol, message)


class WrongClockName(ParserSemanticError):
    def __init__(self, symbol, name):
        message = "Clock name should not be '{}' (must begin with 'clk' followed by a number).".format(
            name)
        super().__init__(symbol, message)


class InvalidInputNumber(ParserSemanticError):
    def __init__(self, symbol):
        message = "Number of inputs must be between 1-16."
        super().__init__(symbol, message)


class AttemptToDefineXORInputs(ParserSemanticError):
    def __init__(self, symbol):
        message = "XOR input number does not need to be specified (2 inputs by default)."
        super().__init__(symbol, message)


class AttemptToDefineNOTInputs(ParserSemanticError):
    def __init__(self, symbol):
        message = "NOT gate input number does not need to be specified (1 input by default)."
        super().__init__(symbol, message)


class AttemptToDefineDTYPEInputs(ParserSemanticError):
    def __init__(self, symbol):
        message = "D-TYPE input number does not need to be specified."
        super().__init__(symbol, message)


class NoDTYPEOutputPortError(ParserSemanticError):
    def __init__(self, symbol):
        message = "D-TYPEs need an output port to be specified."
        super().__init__(symbol, message)


class InvalidBlockHeader(ParserSemanticError):
    def __init__(self, symbol):
        message = "Invalid block header (expected either 'devices', 'initialise', 'connections' or 'monitor')."
        super().__init__(symbol, message)


class DeviceNotInitialised(ParserSemanticError):
    def __init__(self, symbol, name):
        message = "Device '{}' not initialised with number of inputs.".format(
            name)
        super().__init__(symbol, message)


class SwitchNotInitialised(ParserSemanticError):
    def __init__(self, symbol, name):
        message = "Switch '{}' not initialised with initial state.".format(
            name)
        super().__init__(symbol, message)


class ClockNotInitialised(ParserSemanticError):
    def __init__(self, symbol, name):
        message = "Clock '{}' not initialised with clock length.".format(name)
        super().__init__(symbol, message)


class NotInitialisedError(ParserSemanticError):
    def __init__(self, symbol):
        super().__init__(symbol, "")


class ConnectionPresent(ParserSemanticError):
    def __init__(self, symbol, name, suffix):
        if suffix:
            message = "Input '{}.{}' already connected to an output".format(
                name, suffix)
        else:
            message = "Input '{}' already connected to an output".format(name)
        super().__init__(symbol, message)
# ===========================================================================================================
# ===========================================================================================================

# Syntax errors


class InvalidBlockHeaderOrder(ParserSyntaxError):
    def __init__(self, symbol):
        message = "Block headers should be initialised in this order: 'devices', 'initialise', 'connections', 'monitor'."
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


class InvalidInitDeviceRule(ParserSyntaxError):
    def __init__(self, symbol):
        message = "Invalid initialise statement (expected ',' or 'has'/'have')."
        super().__init__(symbol, message)


class InvalidInitSwitchRule(ParserSyntaxError):
    def __init__(self, symbol):
        message = "Invalid initialise statement (expected ',' or 'is'/'are')."
        super().__init__(symbol, message)


class InvalidInitClockRule(ParserSyntaxError):
    def __init__(self, symbol):
        message = "Invalid initialise statement (expected ',' or 'cycle'/'cycle length')."
        super().__init__(symbol, message)


class DeviceTypeError(ParserSyntaxError):
    def __init__(self, symbol):
        message = "Expected a device type."
        super().__init__(symbol, message)


class InvalidDeviceName(ParserSyntaxError):
    def __init__(self, symbol):
        message = "Expected a device name."
        super().__init__(symbol, message)


class InvalidClockName(ParserSyntaxError):
    def __init__(self, symbol):
        message = "Expected a clock name."
        super().__init__(symbol, message)


class InvalidSwitchName(ParserSyntaxError):
    def __init__(self, symbol):
        message = "Expected a switch name."
        super().__init__(symbol, message)


class InvalidSwitchState(ParserSyntaxError):
    def __init__(self, symbol):
        message = "Expected 'HIGH' or 'LOW'."
        super().__init__(symbol, message)


class InputNumberMissing(ParserSyntaxError):
    def __init__(self, symbol):
        message = "Expected an input number between 1 and 16."
        super().__init__(symbol, message)


class InputsDefinedIncorrectly(ParserSyntaxError):
    def __init__(self, symbol):
        message = "Expected 'input' or 'inputs."
        super().__init__(symbol, message)


class ConnectedToError(ParserSyntaxError):
    def __init__(self, symbol):
        message = "Expected 'to' or 'is connected to'."
        super().__init__(symbol, message)


class OutputPortError(ParserSyntaxError):
    def __init__(self, symbol):
        message = "Invalid output port."
        super().__init__(symbol, message)


class InputPortError(ParserSyntaxError):
    def __init__(self, symbol):
        message = "Invalid input port."
        super().__init__(symbol, message)


class DotError(ParserSyntaxError):
    def __init__(self, symbol):
        message = "Invalid output port."
        super().__init__(symbol, message)


class ExtraInfoAfterMonitors(ParserSyntaxError):
    def __init__(self, symbol):
        message = "Extra information after monitors block. Expected nothing."
        super().__init__(symbol, message)
