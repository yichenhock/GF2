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