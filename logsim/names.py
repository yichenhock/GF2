"""Map variable names and string names to unique integers.

Used in the Logic Simulator project. Most of the modules in the project
use this module either directly or indirectly.

Classes
-------
Names - maps variable names and string names to unique integers.
"""


from cgitb import lookup


class Names:

    """Map variable names and string names to unique integers.

    This class deals with storing grammatical keywords and user-defined words,
    and their corresponding name IDs, which are internal indexing integers. It
    provides functions for looking up either the name ID or the name string.
    It also keeps track of the number of error codes defined by other classes,
    and allocates new, unique error codes on demand.

    Parameters
    ----------
    No parameters.

    Public methods
    -------------
    unique_error_codes(self, num_error_codes): Returns a list of unique integer
                                               error codes.

    query(self, name_string): Returns the corresponding name ID for the
                        name string. Returns None if the string is not present.

    lookup(self, name_string_list): Returns a list of name IDs for each
                        name string. Adds a name if not already present.

    get_name_string(self, name_id): Returns the corresponding name string for
                        the name ID. Returns None if the ID is not present.
    """

    def __init__(self):
        """Initialise names list."""

        self.names = []
        self.error_code_count = 0  # How many error codes have been declared

    def unique_error_codes(self, num_error_codes):
        """Return a list of unique integer error codes."""

        if not isinstance(num_error_codes, int):
            raise TypeError("Expected num_error_codes to be an integer.")
        if num_error_codes < 1:
            raise ValueError("Expected name_id to be positive and non-zero.")

        self.error_code_count += num_error_codes
        return range(self.error_code_count - num_error_codes,
                     self.error_code_count)

    def query(self, name_string):
        """Return the corresponding name ID for name_string.
        If the name string is not present in the names list, return None."""

        if not isinstance(name_string, str):
            raise TypeError("Expected name_string to be a string.")
        
        for i in range(len(self.names)):
            if name_string == self.names[i]: 
                return i
        
        return None

    def lookup(self, name_string_list):
        """Return a list of name IDs for each name string in name_string_list.
        If the name string is not present in the names list, add it."""

        if not isinstance(name_string_list, list):
            raise TypeError("Expected name_string_list to be a list.")

        name_id_list = []
        
        for name in name_string_list:
            if not isinstance(name, str):
                raise TypeError("Expected contents of list to be a string.")
            
            in_list = False
            for i in range(len(self.names)):
                if name == self.names[i]:
                    name_id_list.append(i)
                    in_list = True
                    break

            if in_list is False:
                name_id_list.append(len(self.names)) 
                self.names.append(name)

        return name_id_list


    def get_name_string(self, name_id):
        """Return the corresponding name string for name_id.
        If the name_id is not an index in the names list, return None."""
        
        if not isinstance(name_id, int):
            raise TypeError("Expected name_id to be an integer.")
        if name_id < 0:
            raise ValueError("Expected name_id to be positive.")

        if name_id < len(self.names): 
            return self.names[name_id]
        else:
            return None