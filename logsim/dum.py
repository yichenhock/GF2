"""Initialise dummy constants to go into the network, monitors and devices

Contains NO error checks!
"""

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser

from scanner import Symbol

names = Names()
devices = Devices(names)
network = Network(names, devices)
monitors = Monitors(names, devices, network)

class DummyParser: 
    def __init__(self, names, devices, network, monitors, scanner):
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner

        self.name_symbols = []  # [name_symbol, ...]
        self.input_symbols = []  # [(name_symbol, input_suffix_symbol), ...]
        # self.output_symbol = None  # (name_symbol, output_suffix_symbol)
        self.signal_symbols = []  # [(name_symbol, suffix_symbol), ...]
        self.defined_device_ids = {}  # {device_id: device_type}
        self.number_inputs = {}  # {device_id: number_inputs}
        # number_inputs for AND, NAND, OR, NOR only

        self.names.names = ['']

        name_symbol1 = Symbol()
        name_symbol1.id = 1
        name_symbol1.type = Scanner.NAME
        self.name_symbols.append(name_symbol1)

        input_symbol1 = Symbol()
        input_symbol1.id = 2
        name_symbol1.type = Scanner.NAME
        self.input_symbols.append(input_symbol1)

        signal_symbol1 = Symbol()
        signal_symbol1.id = 3
        signal_symbol1.type = Scanner.NAME
        self.signal_symbols.append()


    def make_clock(self, period: int, period_symbol: Symbol) -> None:
        for symbol in self.name_symbols:
            self.defined_device_ids[symbol.id] = self.devices.CLOCK
            self.devices.make_device(
                symbol.id, self.devices.CLOCK, period)

    def make_switch(self, initial_state: int) -> None:
        for symbol in self.name_symbols:
            self.defined_device_ids[symbol.id] = self.devices.SWITCH
            self.devices.make_device(
                symbol.id, self.devices.SWITCH, initial_state)


    def make_gate(self, gate_type: int, number_inputs: int,
                  number_inputs_symbol: Symbol) -> None:
        for symbol in self.name_symbols:
            self.defined_device_ids[symbol.id] = gate_type
            self.number_inputs[symbol.id] = number_inputs
            self.devices.make_device(
                symbol.id, gate_type, number_inputs)

    def make_dtype(self):
        for symbol in self.name_symbols:
            self.defined_device_ids[symbol.id] = self.devices.D_TYPE
            self.devices.make_device(symbol.id, self.devices.D_TYPE)

    def make_xor(self): 
        for symbol in self.name_symbols:
            self.defined_device_ids[symbol.id] = self.devices.XOR
            self.devices.make_device(symbol.id, self.devices.XOR)

    def make_connections(self): 
        for input_symbol in self.input_symbols:
            self.network.make_connection(
                input_symbol[0].id,
                input_symbol[1].id,
                self.output_symbol[0].id,
                None if self.output_symbol[1] is None else
                self.output_symbol[1].id
            )

    def make_monitors(self): 
        for signal_symbol in self.signal_symbols:
            self.monitors.make_monitor(
                    signal_symbol[0].id,
                    None if signal_symbol[1] is None else signal_symbol[1].id
                )