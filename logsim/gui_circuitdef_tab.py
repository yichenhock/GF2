import sys
import wx

class CircuitDefTab(wx.Panel):
    """
    A simple wx.Panel class
    """
    #----------------------------------------------------------------------
    def __init__(self, parent, path, statusbar):
        """"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.statusbar = statusbar

        # read circuit_definition file and populate the text control
        text = self.read_file(path)
        
        self.textBox = wx.TextCtrl(self, -1, text, style = wx.NO_BORDER | wx.TE_MULTILINE) 
      
        font_code = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.textBox.SetFont(font_code)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.textBox, wx.EXPAND, wx.EXPAND, 0)

        self.SetSizer(sizer)

        self.Bind(wx.EVT_LEFT_DOWN, self.on_click)
    
    def set_textbox_state(self, state): 
        self.textBox.Enable(state)

    def on_click(self, event): 
        if not self.textBox.IsEnabled(): 
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