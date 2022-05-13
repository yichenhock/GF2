#!/usr/bin/env python3
"""Preliminary exercises for Part IIA Project GF2."""
import sys


def open_file(path):
    """Open and return the file specified by path."""


def get_next_character(input_file):
    """Read and return the next character in input_file."""


def get_next_non_whitespace_character(input_file):
    """Seek and return the next non-whitespace character in input_file."""


def get_next_number(input_file):
    """Seek the next number in input_file.

    Return the number (or None) and the next non-numeric character.
    """


def get_next_name(input_file):
    """Seek the next name string in input_file.

    Return the name string (or None) and the next non-alphanumeric character.
    """


def main():
    """Preliminary exercises for Part IIA Project GF2."""

    # Check command line arguments
    arguments = sys.argv[1:]
    if len(arguments) != 1:
        print("Error! One command line argument is required.")
        sys.exit()

    else:

        print("\nNow opening file...")
        # Print the path provided and try to open the file for reading

        print("\nNow reading file...")
        # Print out all the characters in the file, until the end of file

        print("\nNow skipping spaces...")
        # Print out all the characters in the file, without spaces

        print("\nNow reading numbers...")
        # Print out all the numbers in the file

        print("\nNow reading names...")
        # Print out all the names in the file

        print("\nNow censoring bad names...")
        # Print out only the good names in the file
        # name = MyNames()
        # bad_name_ids = [name.lookup("Terrible"), name.lookup("Horrid"),
        #                 name.lookup("Ghastly"), name.lookup("Awful")]

if __name__ == "__main__":
    main()
