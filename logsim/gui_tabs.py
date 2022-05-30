"""Description of that this does

Classes:
--------
Description of classes

"""
import sys
import wx
import wx.lib.agw.ultimatelistctrl as ULC

from gui_listctrl import ListCtrl

class RedirectText(object):
    def __init__(self,aWxTextCtrl):
        self.out = aWxTextCtrl

    def write(self,string):
        self.out.AppendText(string)

    def flush(self):
        pass

class ConsoleOutTab(wx.Panel):
    """
    A simple wx.Panel class
    """
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.log = wx.TextCtrl(self, wx.ID_ANY, "", style = wx.NO_BORDER | wx.TE_MULTILINE | wx.TOP | wx.TE_READONLY )
        self.commands = wx.TextCtrl(self, wx.ID_ANY, "", size = (wx.MAXIMIZE,22), style = wx.BORDER_DEFAULT | wx.BOTTOM | wx.TE_PROCESS_ENTER)

        redir = RedirectText(self.log)
        sys.stdout = redir

        # format the font in the text controls
        font_code = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.log.SetFont(font_code)
        self.commands.SetFont(font_code)

        self.log.SetBackgroundColour("dark grey")
        self.log.SetForegroundColour("white")

        self.commands.SetBackgroundColour("dark grey")
        self.commands.SetForegroundColour("white")
        self.commands.SetHint('Type commands here')

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.log, wx.EXPAND, wx.EXPAND, 0)
        sizer.Add(self.commands, 0, wx.EXPAND, 0)

        self.SetSizer(sizer)

        self.commands.Bind(wx.EVT_TEXT_ENTER, self.on_command_entered)

    
    def on_command_entered(self, event):
        """Handle the event when the user enters text."""
        text_box_value = self.commands.GetValue()
        text = "".join(["New text box value: ", text_box_value])
        self.commands.Clear()
        # self.canvas.render(text)
        print(text)

class CircuitDefTab(wx.Panel):
    """
    A simple wx.Panel class
    """
    #----------------------------------------------------------------------
    def __init__(self, parent, path, statusbar):
        """"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.statusbar = statusbar#
        self.enabled = False

        # read circuit_definition file and populate the text control
        text = self.read_file(path)
        
        textBox = wx.TextCtrl(self, -1, text, style = wx.NO_BORDER | wx.TE_MULTILINE) 
      
        font_code = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        textBox.SetFont(font_code)

        textBox.Enable(self.enabled)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(textBox, wx.EXPAND, wx.EXPAND, 0)

        self.SetSizer(sizer)

        self.Bind(wx.EVT_LEFT_DOWN, self.on_click)
    
    def on_click(self, event): 
        if not self.enabled: 
            self.statusbar.SetStatusText('Reset the simulation first to edit!')

    def read_file(self, path): 
        try: 
            f = open(path)
        except OSError: 
            print("This file could not be opened, perhaps it doesn't exist")
            sys.exit()

        text = ''
        while True: 
            c = f.read(1)
            text += c
            if c == '':
                break 

        return text

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
        self.switch_list = ListCtrl(self, wx.ID_ANY,
                                      agwStyle=switch_list_style)
        self.switch_list.InsertColumn(0, "Switch")
        self.switch_list.InsertColumn(1, "State")

        switch_id = 0
        initial_state = 0
        index = self.switch_list.InsertStringItem(switch_id, "switch name")
        attr = "switch_" + str(switch_id)
        setattr(self, attr,
                wx.ToggleButton(self.switch_list, wx.ID_ANY,
                                str(initial_state)))
        button = getattr(self, attr)
        if initial_state == 1:
            button.SetValue(True)

        # Right cell is the toggle button
        self.switch_list.SetItemWindow(index, 1, button)
        # Set switch_id attribute so that event handler can access
        # the id
        button.switch_id = switch_id
        # button.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggle)


        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.switch_list, wx.EXPAND, wx.EXPAND, 0)

        self.SetSizer(sizer)

class MonitorsTab(wx.Panel):
    """
    A simple wx.Panel class
    """
    #----------------------------------------------------------------------
    def __init__(self, parent, statusbar):
        """"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.statusbar = statusbar

        switch_list_style = \
            ULC.ULC_REPORT | ULC.ULC_VRULES | \
            ULC.ULC_HRULES | ULC.ULC_SINGLE_SEL | \
            ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
        self.switch_list = ListCtrl(self, wx.ID_ANY,
                                      agwStyle=switch_list_style)
        self.switch_list.InsertColumn(0, "Component")
        self.switch_list.InsertColumn(1, "") # remove from monitor buttons

        switch_id = 0
        index = self.switch_list.InsertStringItem(switch_id, "component name")
        attr = "switch_" + str(switch_id)
        setattr(self, attr,
                wx.ToggleButton(self.switch_list, wx.ID_ANY,
                                str("Remove")))
        button = getattr(self, attr)
        
        # Right cell is the toggle button
        self.switch_list.SetItemWindow(index, 1, button)
        # Set switch_id attribute so that event handler can access
        # the id
        button.switch_id = switch_id
        button.Bind(wx.EVT_TOGGLEBUTTON, self.on_remove)

        self.label_types = wx.StaticText(self, wx.ID_ANY, "Type")
        self.combo_types = wx.ComboBox(self, wx.ID_ANY, choices=['All', 'Device','Switch','Clock'])
        self.combo_types.SetValue("All")
        self.label_names = wx.StaticText(self, wx.ID_ANY, "Name")
        self.combo_names = wx.ComboBox(self, wx.ID_ANY, choices=['A','B','C'])
        self.add_button = wx.Button(self, wx.ID_ANY, 'Add')

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

        # static boxes for layout
        self.static_box = wx.StaticBox(self, wx.ID_ANY, "Add Component To Monitor")
        self.bottom_sizer = wx.StaticBoxSizer(self.static_box, wx.VERTICAL)
        self.bottom_sizer.Add(self.grid_sizer, 0, wx.EXPAND | wx.ALL, 10)
        self.bottom_sizer.Add(self.add_button, 0, wx.CENTER |wx.ALL, 10)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.switch_list, wx.EXPAND, wx.CENTER | wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.bottom_sizer, 0, wx.CENTER | wx.EXPAND | wx.ALL, 10)

        self.SetSizer(sizer)
    
    def on_remove(self, event): 
        self.statusbar.SetStatusText("Device removed.")
