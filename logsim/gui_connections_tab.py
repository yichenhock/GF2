"""
Inputs tab.

Displays all the inputs for the current compiled definition file.
Allows the state of the buttons to be toggled ON and OFF.

Classes
-------
`InputsTab`
"""
import wx
import wx.lib.agw.ultimatelistctrl as ULC

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

        self.connections_list_style = \
            ULC.ULC_REPORT | \
            ULC.ULC_HRULES | ULC.ULC_SINGLE_SEL | \
            ULC.ULC_HAS_VARIABLE_ROW_HEIGHT | \
            ULC.ULC_SHOW_TOOLTIPS
        self.connections_list = ListCtrl(self, wx.ID_ANY,
                                      agwStyle=self.connections_list_style)

        font = wx.Font(wx.FontInfo().Encoding(wx.FONTENCODING_CP950))

        self.connections_list.InsertColumn(0, _(u"Output"))
        self.connections_list.InsertColumn(1, _(u"To"))
        self.connections_list.InsertColumn(2, _(u"Input"))
        self.connections_list.InsertColumn(3, "")  # remove from monitor buttons

        # configure the drop down boxes
        self.label_device = wx.StaticText(self, wx.ID_ANY, _(u"Device"))
        self.label_port = wx.StaticText(self, wx.ID_ANY, _(u"Port"))
        self.label_output = wx.StaticText(self, wx.ID_ANY, _(u"Output"))
        self.label_input = wx.StaticText(self, wx.ID_ANY, _(u"Input*"))
        self.label_input.SetForegroundColour('red')

        self.combo_output_devices = wx.ComboBox(self, wx.ID_ANY,
                                       choices=[],
                                       style=wx.CB_READONLY)
        self.combo_output_ports = wx.ComboBox(self, wx.ID_ANY,
                                       choices=[],
                                       style=wx.CB_READONLY)
        self.combo_input_devices = wx.ComboBox(self, wx.ID_ANY,
                                       choices=[],
                                       style=wx.CB_READONLY)
        self.combo_input_ports = wx.ComboBox(self, wx.ID_ANY,
                                       choices=[],
                                       style=wx.CB_READONLY)

        # # By default (when nothing selected), port selection is disabled
        # self.combo_output_ports.Enable(False)
        # self.combo_input_ports.Enable(False)

        self.blank = wx.StaticText(self, wx.ID_ANY,'')

        self.add_button = wx.Button(self, wx.ID_ANY, _(u"Add"))

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

        self.btn_grid_sizer = wx.FlexGridSizer(1, 1, (5, 5))
        self.btn_grid_sizer.Add(self.add_button, flag=wx.EXPAND)
        self.btn_grid_sizer.AddGrowableRow(0, 1)

        self.warning_text = wx.StaticText(self, wx.ID_ANY, "* Not all inputs have been connected!")
        self.warning_text.SetForegroundColour("red")

        # static boxes for layout
        self.static_box = wx.StaticBox(
            self, wx.ID_ANY, _(u"Add Connection"))
        self.bottom_sizer = wx.StaticBoxSizer(self.static_box, wx.VERTICAL)
        self.bottom_sizer.Add(self.warning_text, 0, wx.ALL, 3)
        self.bottom_sizer.Add(self.grid_sizer, 0, wx.EXPAND | wx.ALL, 10)
        self.bottom_sizer.Add(self.btn_grid_sizer, 0, wx.CENTER | wx.ALL, 10)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.connections_list, wx.EXPAND,
                  wx.CENTER | wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.bottom_sizer, 0, wx.CENTER | wx.EXPAND | wx.ALL, 10)

        self.SetSizer(sizer)

        self.combo_output_devices.Bind(wx.EVT_COMBOBOX, self.on_combo_op_devices_select)
        self.combo_input_devices.Bind(wx.EVT_COMBOBOX, self.on_combo_ip_devices_select)
        self.add_button.Bind(wx.EVT_LEFT_DOWN, self.on_add_button)

    def on_add_button(self, event):
        """Handle the event when the user adds a connection."""
        pass

    def on_remove(self, event):
        """Handle the event when the user removes a connection."""
        button = event.GetEventObject()
    
    def initialise_connections_list(self):
        """Initialise `self.connections_list` with circuit definition file."""
        self.initialise_combo_boxes()

    def initialise_combo_boxes(self):
        """Initialise `combo_names` with a list of all device names."""
        # outputs: all devices (D-types, gates, switches, clocks)
        output_devices = []
        for device in self.devices.devices_list:
            output_devices.append(self.names.get_name_string(device.device_id))
        self.refresh_combo_output_devices(output_devices)

        # inputs: only D-types and gates
        # not switch or clock basically
        input_devices = []
        for device in self.devices.devices_list:
            if device.device_kind != self.devices.SWITCH and \
                    device.device_kind != self.devices.CLOCK:
                input_devices.append(self.names.get_name_string(device.device_id))
        self.refresh_combo_input_devices(input_devices)
        self.combo_output_ports.Enable(False)
        self.combo_input_ports.Enable(False)

    def refresh_combo_output_devices(self, output_devices):
        self.combo_output_devices.Clear()
        for device in output_devices: 
            self.combo_output_devices.Append(device)

    def refresh_combo_input_devices(self, input_devices):
        self.combo_input_devices.Clear()
        for device in input_devices: 
            self.combo_input_devices.Append(device)

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

    def on_combo_ip_devices_select(self, event):
        """Handles the event when user selects an input device."""
        name = self.combo_input_devices.GetValue()
        device = self.devices.get_device(self.names.query(name))
        self.combo_input_ports.Clear()
        if device.device_kind == self.devices.NOT: 
            # no port selection for NOT gates
            self.combo_input_ports.Enable(False)
        elif device.device_kind == self.devices.D_TYPE:
            possible_ports = ['DATA','CLK','SET','CLEAR']
            self.combo_input_ports.Enable(True)
            for port in possible_ports:
                self.combo_input_ports.Append(port)
                print(port)
        else: # some other gate
            self.combo_input_ports.Enable(True)
            # get the number of inputs the gate has
            # add the inputs to the combo box
            pass

    def append_to_connections_list(self, connection):
        """Add an entry to `self.connections_list`."""
        # connection = [output, output_port, input, input_port]
        pass

    def clear_connections_list(self):
        pass

        # index = self.monitors_list.InsertStringItem(
        #     len(self.displayed_signals), signal)
        # attr = "connection_"
        # setattr(self, attr,
        #         wx.ToggleButton(self.monitors_list, wx.ID_ANY,
        #                         str(_(u"Remove"))))
        # button = getattr(self, attr)
        # # Right cell is the remove button
        # self.monitors_list.SetItemWindow(index, 3, button)
        # # Set switch_id attribute so that event handler can access
        # # the id
        # # button.signal_id = signal_id
        # # button.output_id = output_id
        # button.Bind(wx.EVT_TOGGLEBUTTON, self.on_remove)

        # # self.displayed_signals.append((signal_id, output_id))

    def enable_connections(self, state):
        """Allow connections to be added."""

        self.combo_output_devices.Enable(state)
        self.combo_output_ports.Enable(False)
        self.combo_input_devices.Enable(state)
        self.combo_input_ports.Enable(False)

        self.initialise_combo_boxes()

        self.add_button.Enable(state)

        if state:
            self.warning_text.SetLabel('')
        else:
            self.warning_text.SetLabel(
                _(u" Reset simulation to add connections!"))
