"""."""


class ParserError(Exception):
    """."""

    def __init__(self, symbol, message):
        """."""
        self.symbol = symbol
        self.message = message

    def __eq__(self, error2):
        """."""
        return isinstance(self, type(error2)) and \
            self.symbol == error2.symbol and \
            self.message == error2.message


class ParserSyntaxError(ParserError):
    """."""

    pass


class ParserSyntaxError(ParserError):
    """."""

    pass
