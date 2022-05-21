#!/usr/bin/env python3
"""Preliminary exercises for Part IIA Project GF2."""

import sys
from mynames import MyNames

def open_file(path):
    """Open and return the file specified by path."""

    try: 
        f = open(path)
    except OSError: 
        print("This file could not be opened, perhaps it doesn't exist")
        sys.exit()

    return f


def get_next_character(input_file):
    """Read and return the next character in input_file."""
    return input_file.read(1)

def get_next_non_whitespace_character(input_file):
    """Seek and return the next non-whitespace character in input_file."""
    while True: 
        c = input_file.read(1)
        if not c.isspace():
            return c

def get_next_number(input_file):
    """Seek the next number in input_file.

    Return the number (or None) and the next non-numeric character.
    """
    number = ''
    while True:
        c = input_file.read(1)
        if c.isdigit(): 
            number += c
        else: 
            if number == '':
                number = None
            return number, c 

def get_next_name(input_file):
    """Seek the next name string in input_file.

    Return the name string (or None) and the next non-alphanumeric character.
    """
    name = ''
    in_name = False

    while True: 
        c = input_file.read(1)
        
        if in_name: 
            if c.isalnum(): 
                name += c 
            else: 
                return name, c
        else: 
            if c.isalpha():
                in_name = True 
                name += c 
            elif c == '':
                return None, ''

def main():
    """Preliminary exercises for Part IIA Project GF2."""

    # Check command line arguments
    arguments = sys.argv[1:]
    if len(arguments) != 1:
        print("Error! One command line argument is required.")
        sys.exit()

    else:

        path = arguments[0]
        print("\nNow opening file...")
        # Print the path provided and try to open the file for reading
        file = open_file(path)

        print("\nNow reading file...")
        # Print out all the characters in the file, until the end of file
        while True: 
            c = get_next_character(file)
            if c == '':
                break 
            else: 
                print(c, end='')

        print("\nNow skipping spaces...")
        # Print out all the characters in the file, without spaces
        file.seek(0)
        while True: 
            c = get_next_non_whitespace_character(file)
            if c == '': 
                break 
            else: 
                print(c, end='')

        print("\nNow reading numbers...")
        # Print out all the numbers in the file
        file.seek(0)
        while True: 
            number, c = get_next_number(file)
            if number: 
                print(number)
            if c == '':
                break

        print("\nNow reading names...")
        # Print out all the names in the file
        file.seek(0)
        while True:
            name, c = get_next_name(file)
            if name: 
                print(name)
            if c == '': 
                break

        print("\nNow censoring bad names...")
        # Print out only the good names in the file
        name = MyNames()
        bad_name_ids = [name.lookup("Terrible"), name.lookup("Horrid"),
                        name.lookup("Ghastly"), name.lookup("Awful")]

        file.seek(0)
        while True:
            n, c = get_next_name(file)
            if n and name.lookup(n) not in bad_name_ids: 
                print(n)

            if c == '': 
                break
        file.close()

if __name__ == "__main__":
    main()