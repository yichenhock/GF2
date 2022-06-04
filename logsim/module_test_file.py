#This file is for testing various functions developed in each module
import sys
from names import Names
from scanner import Scanner
from parse import Parser
from devices import Devices
from network import Network
from monitors import Monitors

"""names.py tests"""

# name = Names()
# print(type(name))
# name.lookup(["Hello", "hi"])
# print(name.names)
# print(name.unique_error_codes(1))
# print(name.error_code_count)
# print(name.unique_error_codes(1))
# print(name.error_code_count)
# print(name.query("hi"))
# print(name.get_name_string(1))
# print(name.lookup(["hi", "Whatsup", "hi", "Hello"]))
# print(name.names)

"""scanner.py tests"""

names = Names()
names.lookup(["Hello", "hi"])

# Check command line arguments
arguments = sys.argv[1:]
if len(arguments) != 1:
    print("Error! One command line argument is required.")
    sys.exit()

else:
    path = arguments[0]
    print("\nNow opening file...")
    scanner = Scanner(path, names)

print(scanner.file.read())
scanner.file.seek(0)
x = scanner.get_symbol()
print(x.line_number, x.line_position, x.type, x.id)
type_id_list = []
while x.type != 9:
    x = scanner.get_symbol()
    type_id_list.append([x.type, x.id])
    print(x.line_number, x.line_position, x.type, x.id)
    # print(name.names)

#print(type_id_list)

# """parser.py tests"""
# devices = Devices(names)
# network = Network(names, devices)
# monitors = Monitors(names, devices, network)

# parse = Parser(names, devices, network, monitors, scanner)
# parse.parse_network()
