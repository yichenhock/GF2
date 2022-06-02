
import wx
import wx.lib.agw.ultimatelistctrl as ULC

from gui_listctrl import ListCtrl


class InputsTab(wx.Panel):
    """
    A simple wx.Panel class
    """
    # ----------------------------------------------------------------------

    def __init__(self, parent, names, devices, canvas, statusbar):
        """"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.names = names
        self.devices = devices
        self.canvas = canvas
        self.statusbar = statusbar

        switch_list_style = \
            ULC.ULC_REPORT | \
            ULC.ULC_HRULES | ULC.ULC_SINGLE_SEL | \
            ULC.ULC_HAS_VARIABLE_ROW_HEIGHT | ULC.ULC_NO_HIGHLIGHT | \
            ULC.ULC_SHOW_TOOLTIPS | ULC.ULC_NO_HEADER
        self.switch_list = ListCtrl(self, wx.ID_ANY,
                                    agwStyle=switch_list_style)
        self.switch_list.InsertColumn(0, "Switch")
        self.switch_list.InsertColumn(1, "State")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.switch_list, wx.EXPAND, wx.EXPAND, 0)

        self.SetSizer(sizer)

        self.refresh_list()

    def refresh_list(self):
        self.switch_list.DeleteAllItems()
        switch_ids = self.devices.find_devices(self.devices.SWITCH)

        for i in range(len(switch_ids)):
            switch_id = switch_ids[i]

            state = self.devices.get_device(switch_id).switch_state
            self.append_to_switch_list(i, switch_id, state)

    def append_to_switch_list(self, i: int, switch_id: int,
                              initial_state: int):

        switch_name = self.names.get_name_string(switch_id)

        state = initial_state == 1

        if state:
            button_label = "ON"
        else:
            button_label = "OFF"

        index = self.switch_list.InsertStringItem(i, switch_name)
        attr = "switch_" + str(switch_id)
        setattr(self, attr,
                wx.ToggleButton(self.switch_list, wx.ID_ANY,
                                button_label))
        button = getattr(self, attr)

        button.SetValue(state)
        if state:
            button.SetForegroundColour('green')
        else:
            button.SetForegroundColour('red')

        # Right cell is the toggle button
        self.switch_list.SetItemWindow(index, 1, button)
        # Set switch_id attribute so that event handler can access
        # the id
        button.switch_id = switch_id
        button.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggle)

        self.canvas.render_signals(flush_pan=True)

    def on_toggle(self, event):
        state = event.GetEventObject().GetValue()
        switch_id = event.GetEventObject().switch_id
        if state:
            event.GetEventObject().SetLabel("ON")
            self.statusbar.SetStatusText("Set switch {} to 1.".format(
                self.names.get_name_string(switch_id)))
            self.devices.set_switch(switch_id, 1)
            print("Switch {} set to 1.".format(
                self.names.get_name_string(switch_id)))
            event.GetEventObject().SetForegroundColour('green')
        else:
            event.GetEventObject().SetLabel("OFF")
            self.statusbar.SetStatusText("Set switch {} to 0.".format(
                self.names.get_name_string(switch_id)))
            print("Switch {} set to 0.".format(
                self.names.get_name_string(switch_id)))
            self.devices.set_switch(switch_id, 0)
            event.GetEventObject().SetForegroundColour('red')
