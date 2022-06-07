"""
Tab showing the list of monitored components.

Allows the user to add/remove components easily.
Changes will reflect immediately in the signal trace output.

Classes
-------
`MonitorsTab`
"""
import wx
import wx.lib.agw.ultimatelistctrl as ULC
from gui_listctrl import ListCtrl


class MonitorsTab(wx.Panel):
    """A wx.Panel class to display an editable list of monitored components."""

    def __init__(self, parent, names, devices, monitors, canvas, statusbar):
        """Initialise the panel with use variables and sub-widgets."""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.names = names
        self.devices = devices
        self.monitors = monitors
        self.canvas = canvas
        self.statusbar = statusbar

        # list of signal ids of signals currently being displayed
        self.displayed_signals = []  # [(signal_name, output_port)]

        self.monitors_list_style = \
            ULC.ULC_REPORT | \
            ULC.ULC_HRULES | ULC.ULC_SINGLE_SEL | \
            ULC.ULC_HAS_VARIABLE_ROW_HEIGHT | ULC.ULC_NO_HEADER | \
            ULC.ULC_SHOW_TOOLTIPS
        self.monitors_list = ListCtrl(self, wx.ID_ANY,
                                      agwStyle=self.monitors_list_style)

        font = wx.Font(wx.FontInfo().Encoding(wx.FONTENCODING_CP950))

        self.monitors_list.InsertColumn(0, "Component")
        self.monitors_list.InsertColumn(1, "")  # remove from monitor buttons

        # configure the drop down boxes
        self.label_types = wx.StaticText(self, wx.ID_ANY, _(u"Type"))
        self.label_types.SetFont(font)
        self.combo_types = wx.ComboBox(self, wx.ID_ANY,
                                       choices=[_(u"ALL"),
                                                _(u"GATE"),
                                                _(u"SWITCH"),
                                                _(u"CLOCK"),
                                                _(u"D-TYPE")],
                                       style=wx.CB_READONLY)
        self.combo_types.SetFont(font)
        self.label_names = wx.StaticText(self, wx.ID_ANY, _(u"Name"))
        self.combo_names = wx.ComboBox(
            self, wx.ID_ANY, choices=[], style=wx.CB_READONLY)
        self.add_button = wx.Button(self, wx.ID_ANY, _(u"Add"))
        self.add_all_button = wx.Button(self, wx.ID_ANY, _(u"Add All"))

        # initialise the combo boxes with default values
        self.combo_types.SetValue(_(u"ALL"))

        # Create a sizer.
        self.grid_sizer = wx.FlexGridSizer(2, 2, (5, 5))
        self.grid_sizer.Add(self.label_types, flag=wx.EXPAND)
        self.grid_sizer.Add(self.combo_types, flag=wx.EXPAND)
        self.grid_sizer.Add(self.label_names, flag=wx.EXPAND)
        self.grid_sizer.Add(self.combo_names, flag=wx.EXPAND)

        self.grid_sizer.AddGrowableRow(0, 1)
        self.grid_sizer.AddGrowableRow(1, 1)
        self.grid_sizer.AddGrowableCol(0, 1)
        self.grid_sizer.AddGrowableCol(1, 4)

        self.btn_grid_sizer = wx.FlexGridSizer(1, 2, (5, 5))
        self.btn_grid_sizer.Add(self.add_button, flag=wx.EXPAND)
        self.btn_grid_sizer.Add(self.add_all_button, flag=wx.EXPAND)
        self.btn_grid_sizer.AddGrowableRow(0, 1)
        self.btn_grid_sizer.AddGrowableCol(0, 1)

        self.warning_text = wx.StaticText(self, wx.ID_ANY, "")
        self.warning_text.SetForegroundColour("red")

        # static boxes for layout
        self.static_box = wx.StaticBox(
            self, wx.ID_ANY, _(u"Add Component To Monitor"))
        self.bottom_sizer = wx.StaticBoxSizer(self.static_box, wx.VERTICAL)
        self.bottom_sizer.Add(self.warning_text, 0, wx.ALL, 3)
        self.bottom_sizer.Add(self.grid_sizer, 0, wx.EXPAND | wx.ALL, 10)
        self.bottom_sizer.Add(self.btn_grid_sizer, 0, wx.CENTER | wx.ALL, 10)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.monitors_list, wx.EXPAND,
                  wx.CENTER | wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.bottom_sizer, 0, wx.CENTER | wx.EXPAND | wx.ALL, 10)

        self.SetSizer(sizer)

        self.combo_types.Bind(wx.EVT_COMBOBOX, self.on_combo_type_select)
        self.add_button.Bind(wx.EVT_LEFT_DOWN, self.on_add_button)
        self.add_all_button.Bind(wx.EVT_LEFT_DOWN, self.on_add_all_button)

    def on_combo_type_select(self, event):
        """Update `combo_names` when a component type is selected."""
        if self.combo_types.GetValue() == _(u"ALL"):
            self.initialise_combo_names()

        elif self.combo_types.GetValue() == _(u"GATE"):
            gate_ids = []
            gate_ids.extend(self.devices.find_devices(self.devices.AND))
            gate_ids.extend(self.devices.find_devices(self.devices.OR))
            gate_ids.extend(self.devices.find_devices(self.devices.NAND))
            gate_ids.extend(self.devices.find_devices(self.devices.NOR))
            gate_ids.extend(self.devices.find_devices(self.devices.XOR))
            gate_ids.extend(self.devices.find_devices(self.devices.NOT))

            self.refresh_combo_names(
                [self.names.get_name_string(id) for id in gate_ids])

        elif self.combo_types.GetValue() == _(u"SWITCH"):
            switch_ids = self.devices.find_devices(self.devices.SWITCH)
            self.refresh_combo_names(
                [self.names.get_name_string(id) for id in switch_ids])

        elif self.combo_types.GetValue() == _(u"CLOCK"):
            clock_ids = self.devices.find_devices(self.devices.CLOCK)
            self.refresh_combo_names(
                [self.names.get_name_string(id) for id in clock_ids])

        elif self.combo_types.GetValue() == _(u"D-TYPE"):  # DTYPE IS SPECIAL!
            dtype_ids = self.devices.find_devices(self.devices.D_TYPE)
            self.refresh_combo_names(
                [self.names.get_name_string(id) for id in dtype_ids])

    def clear_monitor_list(self):
        """Clear monitor list before initialisation."""
        # clear the existing stuff on the list
        for (signal_id, output_id) in self.displayed_signals[::-1]:
            signal = self.get_signal_full_name(signal_id, output_id)
            index = self.monitors_list.FindItem(-1, signal)
            self.monitors_list.DeleteItem(index)
            self.displayed_signals.remove((signal_id, output_id))

    # initialise the stuff that is monitored from the start
    def initialise_monitor_list(self):
        """Initialise `self.monitors_list` with circuit definition file."""
        monitored_signals = self.monitors.get_signal_names()[0]
        for signal in monitored_signals:
            self.append_to_monitors_list(signal)
            signal_id, signal_name, output_id, output_name = \
                self.get_signal_and_output_id(signal)
        self.combo_types.SetValue(_(u"All"))
        self.initialise_combo_names()
        try:
            self.canvas.render_signals(flush_pan=True)
        except Exception as e:
            pass

    def get_signal_and_output_id(self, signal):
        """Get `signal_id` and `output_id` based on signal name."""
        name_arr = signal.split('.')
        signal_name = name_arr[0]
        signal_id = self.names.query(signal_name)

        output_id = None
        output_name = None
        if len(name_arr) > 1:
            output_name = name_arr[1]
            output_id = self.names.query(output_name)

        return signal_id, signal_name, output_id, output_name

    def append_to_monitors_list(self, signal):
        """Add an entry to `self.monitors_list`."""
        # signal name may be a dtype
        signal_id, signal_name, output_id, output_name = \
            self.get_signal_and_output_id(signal)

        index = self.monitors_list.InsertStringItem(
            len(self.displayed_signals), signal)
        attr = "signal_" + str(signal_id) + "_" + str(output_id)
        setattr(self, attr,
                wx.ToggleButton(self.monitors_list, wx.ID_ANY,
                                str(_(u"Remove"))))
        button = getattr(self, attr)
        # Right cell is the remove button
        self.monitors_list.SetItemWindow(index, 1, button)
        # Set switch_id attribute so that event handler can access
        # the id
        button.signal_id = signal_id
        button.output_id = output_id
        button.Bind(wx.EVT_TOGGLEBUTTON, self.on_remove)

        self.displayed_signals.append((signal_id, output_id))
        try:
            self.canvas.render_signals(flush_pan=True)
        except Exception as e:
            pass

    def initialise_combo_names(self):
        """Initialise `combo_names` with a list of all device names."""
        self.refresh_combo_names([self.names.get_name_string(
            device.device_id) for device in self.devices.devices_list])

    def refresh_combo_names(self, names_list):
        """Refresh the list in `combo_names`."""
        self.combo_names.Clear()
        dtype_outputs = ["Q", "QBAR"]
        for name in names_list:
            device = self.devices.get_device(self.names.query(name))
            if device.device_kind == self.devices.D_TYPE:
                # DTYPES have multiple output ports
                for port_name in dtype_outputs:
                    self.combo_names.Append(".".join([name, port_name]))
            else:
                self.combo_names.Append(name)

    def on_add_button(self, event):
        """Handle the event when the user adds a component to monitor."""
        name_to_add = self.combo_names.GetValue()
        if name_to_add == "":
            self.statusbar.SetStatusText(_(u"Select a component first!"))
        else:
            monitored_signals = self.monitors.get_signal_names()[0]
            if name_to_add in monitored_signals:
                self.statusbar.SetStatusText(_(u"Component already added!"))
            else:
                self.add_monitor(name_to_add)

    def on_add_all_button(self, event):
        """Handle the event when the user adds all components to monitor."""
        names_list = self.combo_names.GetItems()

        for name in names_list:
            if name not in self.monitors.get_signal_names()[0]:
                self.add_monitor(name)

    def add_monitor(self, name_to_add):
        """Add components to `self.monitors_list`."""
        signal_id, signal_name, output_id, output_name = \
            self.get_signal_and_output_id(name_to_add)

        self.monitors.make_monitor(signal_id, output_id)
        # append the component to the list
        self.append_to_monitors_list(name_to_add)
        self.statusbar.SetStatusText(_(u"Added component to monitor."))
        print(u'{} added to monitor.'.format(name_to_add))

    def get_signal_full_name(self, signal_id, output_id):
        """Get signal name from `signal_id` and `output_id`."""
        if output_id:
            signal_name = "".join([self.names.get_name_string(
                signal_id), '.', self.names.get_name_string(output_id)])
        else:
            signal_name = self.names.get_name_string(signal_id)
        return signal_name

    def on_remove(self, event):
        """Handle the event when the user removes a component."""
        button = event.GetEventObject()
        signal_id = button.signal_id
        output_id = button.output_id

        signal = self.get_signal_full_name(signal_id, output_id)

        # remove the signal from monitors
        self.monitors.remove_monitor(signal_id, output_id)
        # remove the signal from the monitors list
        print(self.monitors_list.FindItem(-1, signal))
        self.monitors_list.DeleteItem(self.monitors_list
                                      .FindItem(-1, signal))
        self.displayed_signals.remove((signal_id, output_id))
        self.statusbar.SetStatusText(_(u"Component removed from monitor."))
        print(_(u"{} removed from monitor.").format(
            self.names.get_name_string(signal_id)))
        try:
            self.canvas.render_signals(flush_pan=True)
        except Exception as e:
            pass

    def enable_monitor(self, state):
        """Allow components to be added to the monitor."""
        # self.combo_types.Enable(state)
        # self.combo_names.Enable(state)
        # self.add_button.Enable(state)
        # self.add_all_button.Enable(state)
        # if state:
        #     self.warning_text.SetLabel('')
        # else:
        #     self.warning_text.SetLabel(
        #         _(u" Reset simulation to add components!"))
