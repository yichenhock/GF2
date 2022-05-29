"""Description of that this does

Classes:
--------
Description of classes

"""
import sys
import wx


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
        self.commands.SetHint('Type commands here')

        self.log.SetBackgroundColour("dark grey")
        self.log.SetForegroundColour("white")

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

        # txtBox = wx.TextCtrl(self, wx.ID_ANY, "")
        text1 = wx.TextCtrl(self, -1, "components - table of switches and clocks and their states. Need to allow the states to be toggled by the user", style = wx.NO_BORDER | wx.TE_MULTILINE) 
      
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text1, wx.EXPAND, wx.EXPAND, 0)

        self.SetSizer(sizer)

class MonitorsTab(wx.Panel):
    """
    A simple wx.Panel class
    """
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        # txtBox = wx.TextCtrl(self, wx.ID_ANY, "")
        text1 = wx.TextCtrl(self, -1, "List of devices and whether they are being monitored. Checkboxes to add them to monitor", style = wx.NO_BORDER | wx.TE_MULTILINE) 
      
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text1, wx.EXPAND, wx.EXPAND, 0)

        self.SetSizer(sizer)