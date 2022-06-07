"""
Inputs tab.

Displays all the inputs for the current compiled definition file.
Allows the state of the buttons to be toggled ON and OFF.

Classes
-------
`InputsTab`
"""
from operator import not_
import wx
import wx.lib.agw.ultimatelistctrl as ULC

from wx.adv import BitmapComboBox

from gui_listctrl import ListCtrl


class ConnectionsTab(wx.Panel):
    """A wx.Panel class to display an editable list of connections."""

    def __init__(self, parent, names, devices, network, statusbar):
        """Initialise the panel with use variables and sub-widgets."""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.names = names
        self.devices = devices
        self.network = network
        self.statusbar = statusbar

        self.unique_id = 0
        self.displayed_connections = []  # [(id, connection, button), ..]

        self.connections_list_style = \
            ULC.ULC_REPORT | \
            ULC.ULC_HRULES | ULC.ULC_SINGLE_SEL | \
            ULC.ULC_HAS_VARIABLE_ROW_HEIGHT | \
            ULC.ULC_SHOW_TOOLTIPS
        self.connections_list = ListCtrl(self, wx.ID_ANY,
                                         agwStyle=self.connections_list_style)

        font = wx.Font(wx.FontInfo().Encoding(wx.FONTENCODING_CP950))

        self.connections_list.InsertColumn(0, "Output")
        self.connections_list.InsertColumn(1, _(u"To"))
        self.connections_list.InsertColumn(2, _(u"Input"))
        self.connections_list.InsertColumn(
            3, "")  # remove from monitor buttons

        # configure the drop down boxes
        self.label_device = wx.StaticText(self, wx.ID_ANY, _(u"Device"))
        self.label_port = wx.StaticText(self, wx.ID_ANY, _(u"Port"))
        self.label_output = wx.StaticText(self, wx.ID_ANY, _(u"Output"))
        self.label_input = wx.StaticText(self, wx.ID_ANY, _(u"Input"))

        self.tick_bmp = wx.Bitmap(wx.Image('./logsim/imgs/tick.png'))
        self.warning_bmp = wx.Bitmap(wx.Image('./logsim/imgs/warning.png'))

        self.combo_output_devices = BitmapComboBox(self, wx.ID_ANY,
                                                   choices=[],
                                                   style=wx.CB_READONLY)
        self.combo_output_ports = BitmapComboBox(self, wx.ID_ANY,
                                                 choices=[],
                                                 style=wx.CB_READONLY)
        self.combo_input_devices = BitmapComboBox(self, wx.ID_ANY,
                                                  choices=[],
                                                  style=wx.CB_READONLY)
        self.combo_input_ports = BitmapComboBox(self, wx.ID_ANY,
                                                choices=[],
                                                style=wx.CB_READONLY)

        self.blank = wx.StaticText(self, wx.ID_ANY, '')

        self.add_button = wx.Button(self, wx.ID_ANY, _(u"Add"))

        # not all inputs connected / reset simulation to continue
        self.warning_text1 = wx.StaticText(self, wx.ID_ANY, "")
        self.warning_text1.SetForegroundColour("red")

        # combo box fields required
        self.warning_text2 = wx.StaticText(self, wx.ID_ANY, "", size=(200, 20))
        self.warning_text2.SetForegroundColour("red")

        # Create a sizer.
        self.grid_sizer = wx.FlexGridSizer(3, 3, (5, 5))

        self.grid_sizer.AddMany([
            (self.blank, 0, wx.EXPAND),
            (self.label_output, 0, wx.EXPAND),
            (self.label_input, 0, wx.EXPAND),

            (self.label_device, 0, wx.EXPAND),
            (self.combo_output_devices, 0, wx.EXPAND),
            (self.combo_input_devices, 0, wx.EXPAND),

            (self.label_port, 0, wx.EXPAND),
            (self.combo_output_ports, 0, wx.EXPAND),
            (self.combo_input_ports, 0, wx.EXPAND)
        ])

        self.grid_sizer.AddGrowableRow(0, 1)
        self.grid_sizer.AddGrowableRow(1, 1)
        self.grid_sizer.AddGrowableRow(2, 1)

        self.grid_sizer.AddGrowableCol(0, 1)
        self.grid_sizer.AddGrowableCol(1, 1.5)
        self.grid_sizer.AddGrowableCol(2, 1.5)

        self.btn_grid_sizer = wx.FlexGridSizer(1, 2, (5, 5))
        self.btn_grid_sizer.Add(self.warning_text2, flag=wx.EXPAND)
        self.btn_grid_sizer.Add(self.add_button, flag=wx.EXPAND)
        self.btn_grid_sizer.AddGrowableRow(0, 1)
        self.btn_grid_sizer.AddGrowableCol(0, 3)
        self.btn_grid_sizer.AddGrowableCol(1, 1)

        # static boxes for layout
        self.static_box = wx.StaticBox(
            self, wx.ID_ANY, _(u"Add Connection"))
        self.bottom_sizer = wx.StaticBoxSizer(self.static_box, wx.VERTICAL)
        self.bottom_sizer.Add(self.warning_text1, 0, wx.ALL, 3)
        self.bottom_sizer.Add(self.grid_sizer, 0, wx.EXPAND | wx.ALL, 10)
        self.bottom_sizer.Add(self.btn_grid_sizer, 0, wx.CENTER | wx.ALL, 10)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.connections_list, wx.EXPAND,
                  wx.CENTER | wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.bottom_sizer, 0, wx.CENTER | wx.EXPAND | wx.ALL, 10)

        self.SetSizer(sizer)

        self.combo_output_devices.Bind(
            wx.EVT_COMBOBOX, self.on_combo_op_devices_select)
        self.combo_input_devices.Bind(
            wx.EVT_COMBOBOX, self.on_combo_ip_devices_select)
        self.add_button.Bind(wx.EVT_LEFT_DOWN, self.on_add_button)

    def get_full_name(self, device_id, device_port_id):
        device_name = self.names.get_name_string(device_id)
        if device_port_id:
            port_name = self.names.get_name_string(device_port_id)
            return ''.join([device_name, '.', port_name])
        else:
            return device_name

    def initialise_connections_list(self):
        """Initialise `self.connections_list` with circuit definition file."""
        self.clear_connections_list()
        self.refresh_combo_boxes()
        # need to add the existing connections to the list
        for _, connection in self.network.connections.items():
            self.append_to_connections_list(connection)

    def append_to_connections_list(self, connection):
        """Add an entry to `self.connections_list`."""
        (input_id, input_port_id, output_id, output_port_id) = connection
        output_name = self.get_full_name(output_id, output_port_id)
        input_name = self.get_full_name(input_id, input_port_id)

        index = self.connections_list.InsertStringItem(
            len(self.displayed_connections), output_name
        )

        self.connections_list.SetStringItem(index, 1, '--->')
        self.connections_list.SetStringItem(index, 2, input_name)

        attr = "_".join([str(output_id), str(output_port_id),
                         str(input_id), str(input_port_id)])
        setattr(self, attr,
                wx.ToggleButton(self.connections_list, wx.ID_ANY,
                                _(u"Remove")))
        button = getattr(self, attr)
        # set attributes for event handler to access the ids
        button.output_id = output_id
        button.output_port_id = output_port_id
        button.input_id = input_id
        button.input_port_id = input_port_id
        button.Bind(wx.EVT_TOGGLEBUTTON, self.on_remove)
        button.id = self.unique_id

        # Right-most cell is the remove button
        self.connections_list.SetItemWindow(index, 3, button)

        self.displayed_connections.append(
            (self.unique_id, connection, button))
        self.unique_id += 1

    def on_remove(self, event):
        """Handle the event when the user removes a connection."""
        button = event.GetEventObject()
        output_id = button.output_id
        output_port_id = button.output_port_id
        input_id = button.input_id
        input_port_id = button.input_port_id

        id = button.id
        # locate the index of the connection containing the same id
        index = 0
        for i in range(len(self.displayed_connections)):
            if self.displayed_connections[i][0] == id:
                index = i
                break

        self.connections_list.DeleteItem(index)
        del self.displayed_connections[index]
        # NEED TO REMOVE THE CONNECTION FROM THE NETWORK TOO!
        error = self.network.remove_connection(
            output_id, output_port_id, input_id, input_port_id)

        self.statusbar.SetStatusText('Connection removed: {} to {}.'
                                     .format(self.get_full_name(
                                         output_id, output_port_id),
                                         self.get_full_name(
                                         input_id, input_port_id)))
        print('Connection removed: {} to {}.'.format(self.get_full_name(
            output_id, output_port_id),
            self.get_full_name(input_id, input_port_id)))
        self.check_network()

        # reinitialise and refresh the combo boxes
        self.refresh_combo_boxes()

    def refresh_combo_boxes(self):
        """Refresh `combo_names` with a list of all device names.
        Includes the status of whether each input has been connected
        to at least one output.
        """
        # outputs: all devices (D-types, gates, switches, clocks)
        output_devices = []
        for device in self.devices.devices_list:
            output_devices.append(self.names.get_name_string(
                device.device_id))
        self.refresh_combo_output_devices(output_devices)

        # inputs: only D-types and gates
        # not switch or clock basically
        input_devices = []
        for device in self.devices.devices_list:
            if device.device_kind != self.devices.SWITCH and \
                    device.device_kind != self.devices.CLOCK:
                input_devices.append(self.names.get_name_string(
                    device.device_id))
        self.refresh_combo_input_devices(input_devices)
        self.combo_output_ports.Clear()
        self.combo_output_ports.Enable(False)
        self.combo_input_ports.Clear()
        self.combo_input_ports.Enable(False)

    def refresh_combo_output_devices(self, output_devices):
        self.combo_output_devices.Clear()
        for device in output_devices:
            self.combo_output_devices.Append(device)

    def refresh_combo_input_devices(self, input_devices):
        self.combo_input_devices.Clear()
        for device_name in input_devices:
            # show a warning triangle if at least one of its input ports
            # has no connected output
            device_id = self.names.query(device_name)
            device = self.devices.get_device(device_id)
            not_all_connected = False
            for input_id in device.inputs:
                if self.network.get_connected_output(device_id, input_id) \
                        is None:
                    not_all_connected = True

            if not_all_connected:
                self.combo_input_devices.Append(
                    device_name, bitmap=self.warning_bmp)
            else:
                self.combo_input_devices.Append(
                    device_name, bitmap=self.tick_bmp)

    def on_combo_op_devices_select(self, event):
        """Handles the event when user selects an output device."""
        # need to refresh output port combo box
        # only enable if its D-TYPE
        name = self.combo_output_devices.GetValue()
        device = self.devices.get_device(self.names.query(name))
        self.combo_output_ports.Clear()
        if device.device_kind == self.devices.D_TYPE:
            self.combo_output_ports.Enable(True)
            self.combo_output_ports.Append('Q')
            self.combo_output_ports.Append('QBAR')
        else:
            # disable the output port
            self.combo_output_ports.Enable(False)

    def check_input_connected(self, device_id, input_id):
        if self.network.get_connected_output(device_id, input_id) is None:
            return False
        return True

    def on_combo_ip_devices_select(self, event):
        """Handles the event when user selects an input device."""
        name = self.combo_input_devices.GetValue()
        device_id = self.names.query(name)
        device = self.devices.get_device(device_id)
        self.combo_input_ports.Clear()
        if device.device_kind == self.devices.NOT:
            # no port selection for NOT gates
            self.combo_input_ports.Enable(False)
        elif device.device_kind == self.devices.D_TYPE:
            possible_ports = ['DATA', 'CLK', 'SET', 'CLEAR']
            self.combo_input_ports.Enable(True)
            for port in possible_ports:
                port_id = self.names.query(port)
                if self.check_input_connected(device_id, port_id):
                    self.combo_input_ports.Append(port, bitmap=self.tick_bmp)
                else:
                    self.combo_input_ports.Append(
                        port, bitmap=self.warning_bmp)
        else:  # some other gate
            self.combo_input_ports.Enable(True)
            # get the number of inputs the gate has
            num_inputs = len(device.inputs)
            # add the inputs to the combo box
            for n in range(1, num_inputs+1):
                port = 'I'+str(n)
                port_id = self.names.query(port)
                if self.check_input_connected(device_id, port_id):
                    self.combo_input_ports.Append(port, bitmap=self.tick_bmp)
                else:
                    self.combo_input_ports.Append(
                        port, bitmap=self.warning_bmp)

                # self.combo_input_ports.Append('I'+str(n),
                #     bitmap=self.warning_bmp)

    def on_add_button(self, event):
        """Handle the event when the user adds a connection."""
        # check that the fields are valid
        # if the port fields are enabled, it means a value must be selected
        incomplete = False

        if self.combo_input_devices.GetValue() == '' or \
                self.combo_input_devices.GetValue() == '':
            incomplete = True
        if self.combo_input_ports.IsEnabled() and \
                self.combo_input_ports.GetValue() == '':
            incomplete = True
        if self.combo_output_devices.IsEnabled() and \
                self.combo_output_devices.GetValue() == '':
            incomplete = True
        if self.combo_output_ports.IsEnabled() and \
                self.combo_output_ports.GetValue() == '':
            incomplete = True

        if incomplete:
            self.warning_text2.SetLabel('Output and input fields \n'
                                        'incomplete!')
        else:
            self.warning_text2.SetLabel('')
            output_name = self.combo_output_devices.GetValue()
            output_id = self.names.query(output_name)
            output_port = self.combo_output_ports.GetValue()
            output_port_id = self.names.query(output_port)

            input_name = self.combo_input_devices.GetValue()
            input_id = self.names.query(input_name)
            input_port = self.combo_input_ports.GetValue()
            input_port_id = self.names.query(input_port)

            # if all the fields are correct, try to add the connection
            # first check if the connection already exists
            # theres a unique error code in networks to detect this

            # MAKE THE ACTUAL CONNECTION
            error = self.network.make_connection(output_id, output_port_id,
                                                 input_id, input_port_id)

            if error == self.network.INPUT_CONNECTED:
                # if so, throw a warning text
                self.warning_text2.SetLabel(
                    'The specified input already\nhas a connection!')
            else:
                self.warning_text2.SetLabel('')
                self.statusbar.SetStatusText('Connection added: {} to {}.'
                                             .format(self.get_full_name(
                                                 output_id, output_port_id),
                                                 self.get_full_name(
                                                 input_id, input_port_id)))
                print('Connection added: {} to {}.'.format(self.get_full_name(
                    output_id, output_port_id),
                    self.get_full_name(input_id, input_port_id)))

                self.check_network()

                # append to the connections list
                connection = (input_id,
                              input_port_id, output_id, output_port_id)
                self.append_to_connections_list(connection)
                # refresh the combo boxes
                self.refresh_combo_boxes()

    def clear_connections_list(self):
        """Clear monitor list before initialisation."""
        for _ in range(len(self.displayed_connections)):
            self.connections_list.DeleteItem(0)
        self.displayed_connections = []

    def check_network(self):
        print('Checking the network... {}'
              .format(self.network.check_network()))
        if self.network.check_network():
            self.warning_text1.SetLabel(' All inputs connected!')
            self.warning_text1.SetForegroundColour('blue')
            print('All inputs are connected! Simulation ready to run.')
        else:
            self.warning_text1.SetLabel(' Not all inputs are connected!')
            self.warning_text1.SetForegroundColour('red')
            print('Not all inputs are connected! Simulation not ready to run.')

    def enable_connections(self, state):
        """Allow connections to be added."""

        self.combo_output_devices.Enable(state)
        self.combo_output_ports.Enable(False)
        self.combo_input_devices.Enable(state)
        self.combo_input_ports.Enable(False)

        self.refresh_combo_boxes()

        self.add_button.Enable(state)

        # enable/disable the remove buttons too
        for item in self.displayed_connections:
            button = item[2]
            button.Enable(state)

        if state:
            self.check_network()
        else:
            self.warning_text1.SetLabel(
                _(u" Reset simulation to add/remove connections!"))
            self.warning_text1.SetForegroundColour('red')
