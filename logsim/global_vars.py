"""
Global variables defined here.

Classes
-------
`GlobalVars`
"""


class GlobalVars:
    """A class for global variables."""

    def __init__(self):
        """Initialise global variables."""
        self.cycles_completed = 0
        # whether circuit definition file has been edited
        self.def_edited = False
        # whether parse_network() returns True
        self.compilation_success = False
