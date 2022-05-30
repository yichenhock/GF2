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
        
        self.names.lookup(['a', 'sw1', 'sw2'])

        a = Symbol()
        a.id = self.names.query('a')
        a.type = self.scanner.NAME

        init_state1 = 0
        sw1 = Symbol()
        sw1.id = self.names.query('sw1')
        sw1.type = self.scanner.NAME

        init_state2 = 0
        sw2 = Symbol()
        sw2.id = self.names.query('sw2')
        sw2.type = self.scanner.NAME

        # parser
        self.devices.make_device(a.id, self.devices.AND, 2)
        self.devices.make_device(sw1.id, self.devices.SWITCH, init_state1)
        self.devices.make_device(sw2.id, self.devices.SWITCH, init_state2)

        device = self.devices.get_device(a.id)
        print(sw1.id, sw2.id)

        self.network.make_connection(a.id, self.names.query('I1'), sw1.id, None)
        self.network.make_connection(a.id, self.names.query('I2'), sw2.id, None)
        print(device.inputs)

        self.monitors.make_monitor(a.id, None)