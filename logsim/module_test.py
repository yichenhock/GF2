#This file is for testing various functions developed in each module
import sys
from names import Names
from scanner import Symbol, Scanner

"""names.py tests"""

name = Names()
name.lookup(["Hello", "hi"])
print(name.names)
print(name.unique_error_codes(1))
print(name.error_code_count)
print(name.unique_error_codes(1))
print(name.error_code_count)
print(name.query("hi"))
print(name.get_name_string(1))
print(name.lookup(["hi", "Whatsup", "hi", "Hello"]))
print(name.names)

# """scanner.py tests"""

# name = Names()
# name.lookup(["Hello", "hi"])


# # Check command line arguments
# arguments = sys.argv[1:]
# if len(arguments) != 1:
#     print("Error! One command line argument is required.")
#     sys.exit()

# else:
#     path = arguments[0]
#     print("\nNow opening file...")
#     scanner = Scanner(path, name)

# print(scanner.file.read())
# scanner.file.seek(0)
# x = scanner.get_symbol()
# type_id_list = []
# while x.type != 10:
#     x = scanner.get_symbol()
#     type_id_list.append([x.type, x.id])
#     # print(x.type, x.id)
#     # print(name.names)

# #print(type_id_list)