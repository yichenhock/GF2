#!/usr/bin/env python3
"""Preliminary exercises for Part IIA Project GF2."""

import sys


def open_file(path):
    """Open and return the file specified by path."""
    return open(path)


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

        path = arguments[0]
        print("\nNow opening file...")
        # Print the path provided and try to open the file for reading
        try: 
            file = open_file(path)
        except: 
            print("error reading ur file:(")
            sys.exit()


        print("\nNow reading file...")
        # Print out all the characters in the file, until the end of file
        print(file.read())


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

        file.close()


if __name__ == "__main__":
    main()


# #!/usr/bin/env python3
# """Preliminary exercises for Part IIA Project GF2."""
# import sys
# from mynames import MyNames


# def open_file(path):
#     """Open and return the file specified by path."""
#     location = "d:/Files/University/Year 3/Projects/GF2 Software/prelim/"

#     try:
#         f = open(location+path, "r")
#     except OSError:
#         print("This file could not be opened, perhaps it doesn't exist")
#         sys.exit()

#     print("The file name is:", path)

#     return(f)


# def get_next_character(input_file):
#     """Read and return the next character in input_file."""

#     return(input_file.read(1))


# def get_next_non_whitespace_character(input_file):
#     """Seek and return the next non-whitespace character in input_file."""

#     while True:
#         character = input_file.read(1)
#         if character.isspace() is False:
#             return(character)
#         elif character == "":
#             return(character)


# def get_next_number(input_file):
#     """Seek the next number in input_file.
#     Return the number (or None) and the next non-numeric character.
#     """

#     number = ""
#     in_number = False
#     while True:
#         character = input_file.read(1)
#         if character.isdigit() is True:
#             number += character
#             in_number = True
#         else:
#             if in_number is True:
#                 return([number, character])
#             elif character == "":
#                 return(["", ""])


# def get_next_name(input_file):
#     """Seek the next name string in input_file.
#     Return the name string (or None) and the next non-alphanumeric character.
#     """

#     name = ""
#     in_name = False
#     while True:
#         character = input_file.read(1)

#         if in_name is True:
#             if character.isalnum() is True:
#                 name += character
#             else:
#                 return([name, character])

#         else:
#             if character.isalpha() is True:
#                 in_name = True
#                 name += character
#             elif character == "":
#                 return["", ""]


# def main():
#     """Preliminary exercises for Part IIA Project GF2."""

#     # Check command line arguments
#     arguments = sys.argv[1:]

#     if len(arguments) != 1:
#         print("Error! One command line argument is required.")
#         sys.exit()

#     else:

#         print("\nNow opening file...")
#         # Print the path provided and try to open the file for reading

#         current_file = open_file(arguments[0])

#         print("\nNow reading file...")
#         # Print out all the characters in the file, until the end of file

#         while True:
#             x = get_next_character(current_file)
#             if x == "":
#                 break
#             else:
#                 print(x, end="")

#         print("\nNow skipping spaces...")
#         # Print out all the characters in the file, without spaces

#         current_file.seek(0)
#         while True:
#             x = get_next_non_whitespace_character(current_file)
#             if x == "":
#                 break
#             else:
#                 print(x, end="")

#         print("\nNow reading numbers...")
#         # Print out all the numbers in the file

#         current_file.seek(0)
#         no_digit = True
#         while True:
#             x = get_next_number(current_file)
#             if x[1] == "":
#                 if no_digit is True:
#                     print(None)
#                 break
#             else:
#                 print(x[0])
#                 no_digit = False

#         print("\nNow reading names...")
#         # Print out all the names in the file

#         current_file.seek(0)
#         no_name = True
#         while True:
#             x = get_next_name(current_file)
#             if x[1] == "":
#                 if no_name is True:
#                     print(None)
#                 break
#             else:
#                 print(x[0])
#                 no_name = False

#         print("\nNow censoring bad names...")
#         # Print out only the good names in the file

#         current_file.seek(0)
#         name = MyNames()
#         bad_name_ids = [name.lookup("Terrible"), name.lookup("Horrid"),
#                         name.lookup("Ghastly"), name.lookup("Awful")]

#         no_name = True
#         bad_name = False
#         while True:
#             x = get_next_name(current_file)
#             if x[1] == "":
#                 if no_name is True:
#                     print(None)
#                 break
#             else:
#                 for i in range(len(name.names)):
#                     if x[0] == name.get_string(i):
#                         bad_name = True

#                 if bad_name is False:
#                     print(x[0])
#                 else:
#                     bad_name = False
#                 no_name = False


# if __name__ == "__main__":
#     main()
