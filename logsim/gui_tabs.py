"""Description of that this does

Classes:
--------
Description of classes

"""
import sys
import wx
import wx.lib.agw.aui as aui

class ConsoleOutTab(wx.Panel):
    """
    A simple wx.Panel class
    """
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        txtOne = wx.TextCtrl(self, wx.ID_ANY, "Console output appears here", style = wx.NO_BORDER | wx.TE_MULTILINE | wx.TOP)
        txtTwo = wx.TextCtrl(self, wx.ID_ANY, "Type commands here", size = (wx.MAXIMIZE,22), style = wx.BORDER_DOUBLE | wx.BOTTOM )

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(txtOne, wx.EXPAND, wx.EXPAND, 0)
        sizer.Add(txtTwo, 0, wx.EXPAND, 0)

        self.SetSizer(sizer)

class CircuitDefTab(wx.Panel):
    """
    A simple wx.Panel class
    """
    #----------------------------------------------------------------------
    def __init__(self, parent, path):
        """"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        # read circuit_definition file and populate the text control
        text = self.read_file(path)
        
        textBox = wx.TextCtrl(self, -1, text, style = wx.NO_BORDER | wx.TE_MULTILINE) 
      
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(textBox, wx.EXPAND, wx.EXPAND, 0)

        self.SetSizer(sizer)

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

class ComponentsTab(wx.Panel):
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

class DevicesTab(wx.Panel):
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