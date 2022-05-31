from sys import displayhook
import wx 
import wx.lib.agw.ultimatelistctrl as ULC
from gui_listctrl import ListCtrl

class MonitorsTab(wx.Panel):
    """
    A simple wx.Panel class
    """
    #----------------------------------------------------------------------
    def __init__(self, parent, names, devices, monitors, canvas, statusbar):
        """"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.names = names
        self.devices = devices
        self.monitors = monitors
        self.canvas = canvas
        self.statusbar = statusbar

        self.displayed_signals = [] # list of signal ids of signals currently being displayed

        monitors_list_style = \
            ULC.ULC_REPORT | \
            ULC.ULC_HRULES | ULC.ULC_SINGLE_SEL | \
            ULC.ULC_HAS_VARIABLE_ROW_HEIGHT | ULC.ULC_NO_HEADER | ULC.ULC_SHOW_TOOLTIPS
        self.monitors_list = ListCtrl(self, wx.ID_ANY,
                                      agwStyle=monitors_list_style)
        self.monitors_list.InsertColumn(0, "Component")
        self.monitors_list.InsertColumn(1, "") # remove from monitor buttons

        # configure the drop down boxes
        self.label_types = wx.StaticText(self, wx.ID_ANY, "Type")
        self.combo_types = wx.ComboBox(self, wx.ID_ANY, choices=['All', 'Gate','Switch','Clock', 'D-Type'], style = wx.CB_READONLY)
        self.label_names = wx.StaticText(self, wx.ID_ANY, "Name")
        self.combo_names = wx.ComboBox(self, wx.ID_ANY, choices=[], style = wx.CB_READONLY)
        self.add_button = wx.Button(self, wx.ID_ANY, 'Add')
        self.add_all_button = wx.Button(self, wx.ID_ANY, 'Add All')

        # initialise the combo boxes with default values
        self.combo_types.SetValue("All")
        self.initialise_combo_names()
        self.initialise_monitor_list()

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

        self.warning_text = wx.StaticText(self,wx.ID_ANY,"")
        self.warning_text.SetForegroundColour("red")

        # static boxes for layout
        self.static_box = wx.StaticBox(self, wx.ID_ANY, "Add Component To Monitor")
        self.bottom_sizer = wx.StaticBoxSizer(self.static_box, wx.VERTICAL)
        self.bottom_sizer.Add(self.warning_text, 0, wx.ALL, 3)
        self.bottom_sizer.Add(self.grid_sizer, 0, wx.EXPAND | wx.ALL, 10)
        self.bottom_sizer.Add(self.btn_grid_sizer, 0, wx.CENTER |wx.ALL, 10)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.monitors_list, wx.EXPAND, wx.CENTER | wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.bottom_sizer, 0, wx.CENTER | wx.EXPAND | wx.ALL, 10)

        self.SetSizer(sizer)
        
        self.combo_types.Bind(wx.EVT_COMBOBOX, self.on_combo_type_select)
        self.add_button.Bind(wx.EVT_LEFT_DOWN, self.on_add_button)
        self.add_all_button.Bind(wx.EVT_LEFT_DOWN, self.on_add_all_button)

    def on_combo_type_select(self, event):
        if self.combo_types.GetValue() == 'All':
            self.initialise_combo_names()

        elif self.combo_types.GetValue() == 'Gate':
            gate_ids = []
            gate_ids.extend(self.devices.find_devices(self.devices.AND))
            gate_ids.extend(self.devices.find_devices(self.devices.OR))
            gate_ids.extend(self.devices.find_devices(self.devices.NAND))
            gate_ids.extend(self.devices.find_devices(self.devices.NOR))
            gate_ids.extend(self.devices.find_devices(self.devices.XOR))

            self.refresh_combo_names([self.names.get_name_string(id) for id in gate_ids])

        elif self.combo_types.GetValue() == 'Switch':
            switch_ids = self.devices.find_devices(self.devices.SWITCH)
            self.refresh_combo_names([self.names.get_name_string(id) for id in switch_ids])

        elif self.combo_types.GetValue() == 'Clock':
            clock_ids = self.devices.find_devices(self.devices.CLOCK)
            self.refresh_combo_names([self.names.get_name_string(id) for id in clock_ids])

        elif self.combo_types.GetValue() == 'D-Type': # DTYPE IS SPECIAL!
            pass
            # dtype_ids = self.devices.find_devices(self.devices.D_TYPE)
            # input_types = ['CLK', 'SET', 'CLEAR', 'DATA']
            # new_list = []
            # for id in dtype_ids: 
            #     new_list.extend(['.'.join([self.names.get_name_string(id),i]) for i in input_types])
            # self.refresh_combo_names(new_list)

    def initialise_monitor_list(self): # initialise the stuff that is monitored from the start
        monitored_signals = self.monitors.get_signal_names()[0]
        
        for signal in monitored_signals:
            self.append_to_monitors_list(signal)

    def append_to_monitors_list(self, signal_name):
        signal_id = self.names.query(signal_name)
        index = self.monitors_list.InsertStringItem(len(self.displayed_signals), signal_name)
        attr = "signal_" + str(signal_id)
        setattr(self, attr,
                wx.ToggleButton(self.monitors_list, wx.ID_ANY,
                                str("Remove")))
        button = getattr(self, attr)
        # Right cell is the remove button
        self.monitors_list.SetItemWindow(index, 1, button)
        # Set switch_id attribute so that event handler can access
        # the id
        button.signal_id = signal_id
        button.Bind(wx.EVT_TOGGLEBUTTON, self.on_remove)

        self.displayed_signals.append(signal_id)
        self.canvas.render_signals(flush_pan=True)

    def initialise_combo_names(self):
        # THIS DOES NOT WORK WITH DTYPES YET!
        self.refresh_combo_names([self.names.get_name_string(device.device_id) for device in self.devices.devices_list])

    def refresh_combo_names(self, names_list):
        self.combo_names.Clear()
        for name in names_list:
            self.combo_names.Append(name)

    def on_add_button(self, event): 
        name_to_add = self.combo_names.GetValue()
        if name_to_add == "":
            self.statusbar.SetStatusText('Select a component first!')
        else:
            monitored_signals = self.monitors.get_signal_names()[0]
            if name_to_add in monitored_signals: 
                self.statusbar.SetStatusText('Component already added!')
            else: 
                # add the component to the monitor
                name_id = self.names.query(name_to_add) 
                # IF THIS IS DTYPE, THERE NEEDS TO BE A SECOND ARGUMENT!

                self.monitors.make_monitor(name_id, None) 
                # append the component to the list
                self.append_to_monitors_list(name_to_add)
                self.statusbar.SetStatusText('Added component to monitor.')
                print('{} added to monitor.'.format(name_to_add))

    def on_add_all_button(self,event):
        pass

    def on_remove(self, event): 
        signal_id = event.GetEventObject().signal_id
        # remove the signal from monitors
        # NEED TO ACCOUNT FOR DTYPES!!
        self.monitors.remove_monitor(signal_id, None)
        # remove the signal from the monitors list
        self.monitors_list.DeleteItem(self.displayed_signals.index(signal_id))
        self.displayed_signals.remove(signal_id)
        self.statusbar.SetStatusText("Component removed from monitor.")
        print('{} removed from monitor.'.format(self.names.get_name_string(signal_id)))
        self.canvas.render_signals(flush_pan=True)

    def enable_monitor(self, state): 
        self.combo_types.Enable(state)
        self.combo_names.Enable(state)
        self.add_button.Enable(state)
        self.add_all_button.Enable(state)
        if state: 
            self.warning_text.SetLabel('')
        else:
            self.warning_text.SetLabel("*Reset simulation to add components to monitor!")
        