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

        # self.name_symbols = []  # [name_symbol, ...]
        # self.input_symbols = []  # [(name_symbol, input_suffix_symbol), ...]
        # # self.output_symbol = None  # (name_symbol, output_suffix_symbol)
        # self.signal_symbols = []  # [(name_symbol, suffix_symbol), ...]
        # self.defined_device_ids = {}  # {device_id: device_type}
        # self.number_inputs = {}  # {device_id: number_inputs}
        # # number_inputs for AND, NAND, OR, NOR only
        
        self.names.lookup(['a', 'sw1', 'sw2'])

        a = Symbol()
        a.id = self.names.query('a')
        a.type = self.scanner.NAME

        and_gate = Symbol()
        and_gate.id = self.scanner.AND_id
        and_gate.type = self.scanner.KEYWORD

        init_state1 = 0
        sw1 = Symbol()
        sw1.id = self.names.query('sw1')
        sw1.type = self.scanner.KEYWORD

        init_state2 = 2
        sw2 = Symbol()
        sw2.id = self.names.query('sw2')
        sw2.type = self.scanner.KEYWORD
        
        switch = Symbol()
        switch.id = self.scanner.SWITCH_id
        switch.type = self.scanner.KEYWORD

        # parser
        self.devices.make_device(a.id, self.devices.AND, 2)
        self.devices.make_device(sw1.id, self.devices.SWITCH, init_state1)
        self.devices.make_device(sw2.id, self.devices.SWITCH, init_state2)

        self.network.make_connection(sw1.id, None, a.id, input1.id)
        self.network.make_connection(sw2.id, None, a.id, input2.id)

        self.monitors.make_monitor(a.id, output_id)

        # self.input_symbols = [(a, I1), (a, I2), ...]#

        # self.devices.make_device(symbol.id, device_kind, device_property=None)

        # self.network.make_connection(first_device_id, first_port_id, second_device_id,
        #             second_port_id )

        # self.monitors.make_monitor(device_id, output_id)
        #
        # self.devices.set_switch(device_id, signal)

    # def make_clock(self, period: int, period_symbol: Symbol) -> None:
    #     for symbol in self.name_symbols:
    #         self.defined_device_ids[symbol.id] = self.devices.CLOCK
    #         self.devices.make_device(
    #             symbol.id, self.devices.CLOCK, period)

    # def make_switch(self, initial_state: int) -> None:
    #     for symbol in self.name_symbols:
    #         self.defined_device_ids[symbol.id] = self.devices.SWITCH
    #         self.devices.make_device(
    #             symbol.id, self.devices.SWITCH, initial_state)


    # def make_gate(self, gate_type: int, number_inputs: int,
    #               number_inputs_symbol: Symbol) -> None:
    #     for symbol in self.name_symbols:
    #         self.defined_device_ids[symbol.id] = gate_type
    #         self.number_inputs[symbol.id] = number_inputs
    #         self.devices.make_device(
    #             symbol.id, gate_type, number_inputs)

    # def make_dtype(self):
    #     for symbol in self.name_symbols:
    #         self.defined_device_ids[symbol.id] = self.devices.D_TYPE
    #         self.devices.make_device(symbol.id, self.devices.D_TYPE)

    # def make_xor(self): 
    #     for symbol in self.name_symbols:
    #         self.defined_device_ids[symbol.id] = self.devices.XOR
    #         self.devices.make_device(symbol.id, self.devices.XOR)

    # def make_connections(self): 
    #     for input_symbol in self.input_symbols:
    #         self.network.make_connection(
    #             input_symbol[0].id,
    #             input_symbol[1].id,
    #             self.output_symbol[0].id,
    #             None if self.output_symbol[1] is None else
    #             self.output_symbol[1].id
    #         )

    # def make_monitors(self): 
    #     for signal_symbol in self.signal_symbols:
    #         self.monitors.make_monitor(
    #                 signal_symbol[0].id,
    #                 None if signal_symbol[1] is None else signal_symbol[1].id
    #             )