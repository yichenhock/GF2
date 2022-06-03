"""Initialise dummy constants to go into the network, monitors and devices.

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
    """."""

    def __init__(self, names, devices, network, monitors, scanner):
        """."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner
        
        self.names.lookup(['a', 'sw1', 'sw2'])

        self.a = Symbol()
        self.a.id = self.names.query('a')
        self.a.type = self.scanner.NAME

        self.init_state1 = 0
        self.sw1 = Symbol()
        self.sw1.id = self.names.query('sw1')
        self.sw1.type = self.scanner.NAME

        self.init_state2 = 0
        self.sw2 = Symbol()
        self.sw2.id = self.names.query('sw2')
        self.sw2.type = self.scanner.NAME

        self.f = Symbol()
        self.f.id = self.names.query('f')
        self.f.type = self.scanner.NAME

        
    def parse_network(self):
        """."""
        # f = Symbol()
        # f.id = self.names.query('f')
        # f.type = self.scanner.NAME

        # parser
        self.devices.make_device(self.a.id, self.devices.AND, 2)
        self.devices.make_device(self.sw1.id, self.devices.SWITCH, self.init_state1)
        self.devices.make_device(self.sw2.id, self.devices.SWITCH, self.init_state2)

        # self.devices.make_device(f.id, self.devices.D_TYPE)

        # device = self.devices.get_device(a.id)
        # print(sw1.id, sw2.id)

        self.network.make_connection(self.a.id, self.names.query('I1'), self.sw1.id, None)
        self.network.make_connection(self.a.id, self.names.query('I2'), self.sw2.id, None)

        # self.network.make_connection(sw1.id, None, f.id, self.names.query('QBAR'))
        # print(device.inputs)

        self.monitors.make_monitor(self.a.id, None)

        return True
