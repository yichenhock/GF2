"""
Inputs tab.

Displays all the inputs for the current compiled definition file.
Allows the state of the buttons to be toggled ON and OFF.

Classes
-------
InputsTab - A wx.Panel class to display a list of input switches.
"""
import wx
import wx.lib.agw.ultimatelistctrl as ULC

from gui_modules.gui_listctrl import ListCtrl


class InputsTab(wx.Panel):
    """A wx.Panel class to display a list of input switches.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    canvas: the canvas from `gui.py`.
    statusbar: the statusbar from `gui.py`.

    Public methods
    --------------
    refresh_list(self): Refresh the list with inputs from last compiled file.

    append_to_switch_list(self, i, switch_id, initial_state):
                                                    Add a switch to the list.
    """

    # ----------------------------------------------------------------------

    def __init__(self, parent, names, devices, canvas, statusbar):
        """Initialise switch list widget."""
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
        self.switch_list.InsertColumn(0, _(u"Switch"))
        self.switch_list.InsertColumn(1, _(u"State"))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.switch_list, wx.EXPAND, wx.EXPAND, 0)

        self.SetSizer(sizer)

        self.refresh_list()

    def refresh_list(self):
        """Refresh the list with inputs from last compiled file."""
        self.switch_list.DeleteAllItems()
        switch_ids = self.devices.find_devices(self.devices.SWITCH)

        for i in range(len(switch_ids)):
            switch_id = switch_ids[i]

            state = self.devices.get_device(switch_id).switch_state
            self.append_to_switch_list(i, switch_id, state)

    def append_to_switch_list(self, i, switch_id, initial_state):
        """Add a switch to the list."""
        switch_name = self.names.get_name_string(switch_id)

        state = initial_state == 1

        if state:
            button_label = _(u"ON")
        else:
            button_label = _(u"OFF")

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
        button.Bind(wx.EVT_TOGGLEBUTTON, self._on_toggle)

        try:
            self.canvas.render_signals(flush_pan=True)
        except Exception as e:
            pass

    def _on_toggle(self, event):
        """Handle event when user toggles the switch button."""
        state = event.GetEventObject().GetValue()
        switch_id = event.GetEventObject().switch_id
        if state:
            event.GetEventObject().SetLabel(_(u"ON"))
            self.statusbar.SetStatusText(_(u"Set switch {} to 1.").format(
                self.names.get_name_string(switch_id)))
            self.devices.set_switch(switch_id, 1)
            print(_(u"Switch {} set to 1.").format(
                self.names.get_name_string(switch_id)))
            event.GetEventObject().SetForegroundColour('green')
        else:
            event.GetEventObject().SetLabel(_(u"OFF"))
            self.statusbar.SetStatusText(_(u"Set switch {} to 0.").format(
                self.names.get_name_string(switch_id)))
            print(_(u"Switch {} set to 0.").format(
                self.names.get_name_string(switch_id)))
            self.devices.set_switch(switch_id, 0)
            event.GetEventObject().SetForegroundColour('red')
