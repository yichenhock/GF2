
import wx
import wx.lib.agw.ultimatelistctrl as ULC

from gui_listctrl import ListCtrl

class InputsTab(wx.Panel):
    """
    A simple wx.Panel class
    """
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
      
        switch_list_style = \
            ULC.ULC_REPORT | ULC.ULC_VRULES | \
            ULC.ULC_HRULES | ULC.ULC_SINGLE_SEL | \
            ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
        self.monitors_list = ListCtrl(self, wx.ID_ANY,
                                      agwStyle=switch_list_style)
        self.monitors_list.InsertColumn(0, "Switch")
        self.monitors_list.InsertColumn(1, "State")

        switch_id = 0
        initial_state = 0
        index = self.monitors_list.InsertStringItem(switch_id, "switch name")
        attr = "switch_" + str(switch_id)
        setattr(self, attr,
                wx.ToggleButton(self.monitors_list, wx.ID_ANY,
                                str(initial_state)))
        button = getattr(self, attr)
        if initial_state == 1:
            button.SetValue(True)

        # Right cell is the toggle button
        self.monitors_list.SetItemWindow(index, 1, button)
        # Set switch_id attribute so that event handler can access
        # the id
        button.switch_id = switch_id
        # button.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggle)


        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.monitors_list, wx.EXPAND, wx.EXPAND, 0)

        self.SetSizer(sizer)