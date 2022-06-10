"""
Contains inherited classes from Python's builtin Exceptions class.

Classes
-------
ParserError - Base class for all input file processing errors.

ParserSemanticError - Base class for all semantic errors.

ParserSyntaxError - Base class for all syntax errors.


Semantic errors
-------
UndefinedError - Undefined device name.

RedefinedError - A device is defined again in the devices block.

WrongDeviceName - Device defined as a gate but has the name of a switch
                  or clock.

InvalidClockLength - Clock length needs to be an integer between 1 and 1000.

WrongSwitchName - Wrong syntax for switch name.

WrongClockName - Wrong syntax for clock name.

InvalidInputNumber - Expected number of inputs to be between 1-16.

AttemptToDefineXORInputs - User attempts to specify number of XOR inputs.

AttemptToDefineNOTInputs - User attempts to specify number of NOT inputs.

AttemptToDefineDTYPEInputs - User attempts to specify number of DTYPE inputs.

NoDTYPEOutputPortError - Expected DTYPE output port (Q/QBAR).

InvalidBlockHeader - Expected 'devices', 'initialise', 'connections' or
                    'monitors'.

DeviceNotInitialised - A device has not been initialised.

SwitchNotInitialised - A switch has not been initialised.

ClockNotInitialised - A clock has not been initialised.

NotInitialisedError - A device has not been initialised.

ConnectionPresent - User attempts to make a connection to an input port that
                    is already connected.

Syntax errors
-------
InvalidBlockHeaderOrder - Headers are not given in the required syntax order.

SemicolonError - Missing semicolon.

OpenBracketError - Missing open bracket.

CloseBracketError - Missing close bracket.

InvalidDeviceRule - Device definition line is missing 'is'/'are'.

InvalidInitDeviceRule - Gate/DTYPE initialisation line is missing
                        'has'/'have'.

InvalidInitSwitchRule - Switch initialisation line is missing 'is'/'are'.

InvalidInitClockRule - Invalid initialise statement for clocks.

DeviceTypeError - Expected a device type.

InvalidDeviceName - Expected a device name.

InvalidClockName - Expected a clock name of the form 'clk' followed by
                    a number.

InvalidSwitchName - Expected a switch name of the form 'sw' followed
                    by a number.

InvalidSwitchState - Expected 'HIGH' or 'LOW'.

InputNumberMissing - Expected an input number between 1 and 16.

InputsDefinedIncorrectly - Expected 'input' or 'inputs'.

ConnectedToError - Expected in 'to' or 'is connected to'.

OutputPortError - Output port is not 'Q' or 'QBAR' for a DTYPE device.

InputPortError - Input port is name is not valid.

DotError - Missing dot.

ExtraInfoAfterMonitors - Extra information after the closed bracket in the
                        monitors section.
"""


class ParserError(Exception):
    """Base class for all input file processing errors."""

    def __init__(self, symbol, message):
        """Initialise error and its message.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        'message': the error message to be printed.
        """
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


class ParserSyntaxError(ParserError):
    """Base class for all syntax errors."""

# =============================================================================
# =============================================================================

# Semantic errors


class UndefinedError(ParserSemanticError):
    """Undefined device name."""

    def __init__(self, symbol, name):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = "Device '{}' must be defined before use.".format(name)
        super().__init__(symbol, message)


class RedefinedError(ParserSemanticError):
    """A device is defined again in the devices block."""

    def __init__(self, symbol, name):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        'name': the name which is being redefined.
        """
        message = "Device '{}' has been previously defined.".format(name)
        super().__init__(symbol, message)


class WrongDeviceName(ParserSemanticError):
    """Device defined as a gate but has the name of a switch or clock."""

    def __init__(self, symbol, name):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        'name': the name which is wrong.
        """
        message = ("Device name should not be '{}' (must not begin with 'sw' "
                   "or 'clk').").format(name)
        super().__init__(symbol, message)


class InvalidClockLength(ParserSemanticError):
    """Clock length needs to be an integer between 1 and 1000."""

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = "Clock length needs to be an integer between 1 and 1000."
        super().__init__(symbol, message)


class WrongSwitchName(ParserSemanticError):
    """Wrong syntax for switch name."""

    def __init__(self, symbol, name):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        'name': the name which is wrong.
        """
        message = ("Switch name should not be '{}' (must begin with 'sw' "
                   "followed by a number).").format(name)
        super().__init__(symbol, message)


class WrongClockName(ParserSemanticError):
    """Wrong syntax for clock name."""

    def __init__(self, symbol, name):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        'name': the name which is wrong.
        """
        message = ("Clock name should not be '{}' (must begin with 'clk' "
                   "followed by a number).").format(name)
        super().__init__(symbol, message)


class InvalidInputNumber(ParserSemanticError):
    """Expected number of inputs to be between 1-16."""

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = "Number of inputs must be between 1-16."
        super().__init__(symbol, message)


class AttemptToDefineXORInputs(ParserSemanticError):
    """User attempts to specify number of XOR inputs.

    This is always 2 and does not need to be defined.
    """

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = ("XOR input number does not need to be specified (2 "
                   "inputs by default).")
        super().__init__(symbol, message)


class AttemptToDefineNOTInputs(ParserSemanticError):
    """User attempts to specify number of NOT inputs.

    This is always 1 and does not need to be defined.
    """

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = ("NOT gate input number does not need to be specified "
                   "(1 input by default).")
        super().__init__(symbol, message)


class AttemptToDefineDTYPEInputs(ParserSemanticError):
    """User attempts to specify number of DTYPE inputs.

    This is always 4 and does not need to be defined.
    """

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = "D-TYPE input number does not need to be specified."
        super().__init__(symbol, message)


class NoDTYPEOutputPortError(ParserSemanticError):
    """Expected DTYPE output port (Q/QBAR)."""

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = "D-TYPEs need an output port to be specified."
        super().__init__(symbol, message)


class InvalidBlockHeader(ParserSemanticError):
    """Expected 'devices', 'initialise', 'connections' or 'monitors'."""

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = ("Invalid block header (expected either 'devices', "
                   "'initialise', 'connections' or 'monitor').")
        super().__init__(symbol, message)


class DeviceNotInitialised(ParserSemanticError):
    """A device has not been initialised."""

    def __init__(self, symbol, name):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        'name': the name of the device that has not been initialised.
        """
        message = "Device '{}' not initialised with number of inputs.".format(
            name)
        super().__init__(symbol, message)


class SwitchNotInitialised(ParserSemanticError):
    """A switch has not been initialised."""

    def __init__(self, symbol, name):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        'name': the name of the switch that has not been initialised.
        """
        message = "Switch '{}' not initialised with initial state.".format(
            name)
        super().__init__(symbol, message)


class ClockNotInitialised(ParserSemanticError):
    """A clock has not been initialised."""

    def __init__(self, symbol, name):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        'name': the name of the clock that has not been initialised.
        """
        message = "Clock '{}' not initialised with clock length.".format(name)
        super().__init__(symbol, message)


class NotInitialisedError(ParserSemanticError):
    """A device has not been initialised."""

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        super().__init__(symbol, "")


class ConnectionPresent(ParserSemanticError):
    """Attempt to make a connection to an already connected input port.

    One input port can only receive one
    signal, but one output port can be
    split into multiple signals.
    """

    def __init__(self, symbol, name, suffix):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        'name': the name of the device to
        which the port belongs.
        'suffix': the port name which has been
        connected already e.g. I1, CLEAR.
        """
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
    """Headers are not given in the required syntax order."""

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = ("Block headers should be initialised in this order: "
                   "'devices', 'initialise', 'connections', 'monitor'.")
        super().__init__(symbol, message)


class SemicolonError(ParserSyntaxError):
    """Missing semicolon at end of line."""

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = "Expected a ';'"
        super().__init__(symbol, message)


class OpenBracketError(ParserSyntaxError):
    """Missing open bracket."""

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = "Expected a '('"
        super().__init__(symbol, message)


class CloseBracketError(ParserSyntaxError):
    """Missing close bracket."""

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = "Expected a ')'"
        super().__init__(symbol, message)


class InvalidDeviceRule(ParserSyntaxError):
    """Device definition line is missing 'is'/'are'."""

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = "Invalid device statement (expected ',' or 'is'/'are')."
        super().__init__(symbol, message)


class InvalidInitDeviceRule(ParserSyntaxError):
    """Gate/DTYPE initialisation line is missing 'has'/'have'.

    When gates and DTYPES are initialised,
    the number of inputs should be defined.
    """

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = ("Invalid initialise statement (expected ',' "
                   "or 'has'/'have').")
        super().__init__(symbol, message)


class InvalidInitSwitchRule(ParserSyntaxError):
    """Switch initialisation line is missing 'is'/'are'.

    When switches are initialised, the
    initial state should be defined as HIGH/LOW.
    """

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = "Invalid initialise statement (expected ',' or 'is'/'are')."
        super().__init__(symbol, message)


class InvalidInitClockRule(ParserSyntaxError):
    """Invalid initialise statement for clocks."""

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = ("Invalid initialise statement (expected ',' or "
                   "'cycle'/'cycle length').")
        super().__init__(symbol, message)


class DeviceTypeError(ParserSyntaxError):
    """Expected a device type.

    Can be one of the following:
    SWITCH, CLOCK, NOR, NOT, NAND, OR, XOR, AND, DTYPE.
    """

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = "Expected a device type."
        super().__init__(symbol, message)


class InvalidDeviceName(ParserSyntaxError):
    """Expected a device name."""

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = "Expected a device name."
        super().__init__(symbol, message)


class InvalidClockName(ParserSyntaxError):
    """Expected a clock name of the form 'clk' followed by a number."""

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = "Expected a clock name."
        super().__init__(symbol, message)


class InvalidSwitchName(ParserSyntaxError):
    """Expected a switch name of the form 'sw' followed by a number."""

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = "Expected a switch name."
        super().__init__(symbol, message)


class InvalidSwitchState(ParserSyntaxError):
    """Expected 'HIGH' or 'LOW'."""

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = "Expected 'HIGH' or 'LOW'."
        super().__init__(symbol, message)


class InputNumberMissing(ParserSyntaxError):
    """Expected an input number between 1 and 16."""

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = "Expected an input number between 1 and 16."
        super().__init__(symbol, message)


class InputsDefinedIncorrectly(ParserSyntaxError):
    """Expected 'input' or 'inputs'."""

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.

        """
        message = "Expected 'input' or 'inputs."
        super().__init__(symbol, message)


class ConnectedToError(ParserSyntaxError):
    """Expected in 'to' or 'is connected to'."""

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = "Expected 'to' or 'is connected to'."
        super().__init__(symbol, message)


class OutputPortError(ParserSyntaxError):
    """Output port is not 'Q' or 'QBAR' for a DTYPE device."""

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = "Invalid output port."
        super().__init__(symbol, message)


class InputPortError(ParserSyntaxError):
    """Input port is name is not valid.

    This could be because it is not of the form 'I'
    followed by a number for non-DTYPES.

    For DTYPEs, this is because it is not one of
    'CLK', 'SET', 'CLEAR' and 'DATA'.
    If the port is of the form 'I' followed by a number:
    For XOR, this is because the labelled number exceeds 2.
    For NOT, this is because the labelled number exceeds 1.
    For other gates, this could be because the number exceeds
    the defined number of inputs as in the initialise section.
    """

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = "Invalid input port."
        super().__init__(symbol, message)


class DotError(ParserSyntaxError):
    """Missing dot."""

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = "Missing dot in input name.\
            Input names should be of the form device_name.port_name."
        super().__init__(symbol, message)


class ExtraInfoAfterMonitors(ParserSyntaxError):
    """Extra information after the closed bracket in the monitors section."""

    def __init__(self, symbol):
        """Initialise an instance of the class.

        Parameters
        ---------
        'symbol': the symbol on which the error occurs.
        """
        message = "Extra information after monitors block. Expected nothing."
        super().__init__(symbol, message)
