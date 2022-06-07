"""
Tab showing the circuit definition file.

Allows the user to edit the file.

Classes
-------
`CircuitDefTab`
"""
import wx


class CircuitDefTab(wx.Panel):
    """A wx.Panel class to display the circuit definition."""

    # ----------------------------------------------------------------------

    def __init__(self, parent, path, statusbar, global_vars):
        """Initialise the window."""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.statusbar = statusbar
        self.global_vars = global_vars

        self.textBox = wx.TextCtrl(
            self, -1, "", style=wx.NO_BORDER | wx.TE_MULTILINE |
            wx.TE_PROCESS_ENTER)

        font_code = wx.Font(10, wx.MODERN, wx.NORMAL,
                            wx.NORMAL, False, u'Consolas')
        self.textBox.SetFont(font_code)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.textBox, wx.EXPAND, wx.EXPAND, 0)

        self.SetSizer(sizer)
        self.textBox.Bind(wx.EVT_KEY_DOWN, self.on_edit_attempt)
        self.textBox.Bind(wx.EVT_TEXT, self.on_text_edit)

    def on_text_edit(self, event):
        """Set `def_edited` to `True` when user edits the textBox."""
        self.global_vars.def_edited = True
        event.Skip()

    def get_text(self):
        """Get text from `self.textBox`."""
        return self.textBox.GetValue()

    def set_textbox_state(self, state):
        """Format the look of the textBox depending on editablity."""
        self.textBox.SetEditable(state)
        if state:
            self.textBox.SetForegroundColour('black')
            self.textBox.SetBackgroundColour('white')
        else:
            self.textBox.SetForegroundColour('grey')
            self.textBox.SetBackgroundColour('white')

    def on_edit_attempt(self, event):
        """Handle the event the user attempts to edit."""
        if not self.textBox.IsEditable():
            self.statusbar.SetStatusText(
                _(u"Reset the simulation first to edit!"))
        else:
            event.Skip()

    def replace_text(self, new_text):
        """Replace the text with new text."""
        self.textBox.SetValue(new_text)
