"""
Console out/Output tab.

Classes:
--------
`RedirectText`
`ConsoleOutTab`
"""
import sys
import wx


class RedirectText(object):
    """Redirect the console log output to the text ctrl in `ConsoleOutTab`."""

    def __init__(self, aWxTextCtrl):
        """Initialise the output text widget."""
        self.out = aWxTextCtrl

    def write(self, string):
        """Write to output."""
        self.out.AppendText(string)

    def flush(self):
        """Flush output."""
        pass


class ConsoleOutTab(wx.Panel):
    """A wx.Panel class to display the console output."""

    # ----------------------------------------------------------------------

    def __init__(self, parent, path, names, devices, network,
                 monitors, parser, inputsPanel, set_gui_state,
                 global_vars, canvas, save_file):
        """Initialise with useful variables and configure layout."""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.parent = parent
        self.names = names
        self.devices = devices
        self.monitors = monitors
        self.network = network
        self.inputsPanel = inputsPanel
        self.set_gui_state = set_gui_state  # function

        self.path = path
        self.parser = parser
        self.save_file = save_file

        self.canvas = canvas

        self.global_vars = global_vars
        # self.cycles_completed = 0  # number of simulation cycles completed

        self.character = ""  # current character
        self.line = ""  # current string entered by the user
        self.cursor = 0  # cursor position

        self.log = wx.TextCtrl(
            self, wx.ID_ANY, "", style=wx.NO_BORDER | wx.TE_MULTILINE |
            wx.TOP | wx.TE_READONLY)
        self.commands = wx.TextCtrl(self, wx.ID_ANY, "", size=(
            wx.MAXIMIZE, 22), style=wx.BORDER_DEFAULT | wx.BOTTOM |
            wx.TE_PROCESS_ENTER)

        redir = RedirectText(self.log)
        sys.stdout = redir

        # format the font in the text controls
        font_code = wx.Font(10, wx.MODERN, wx.NORMAL,
                            wx.NORMAL, False, u'Consolas')
        self.log.SetFont(font_code)
        self.commands.SetFont(font_code)

        self.log.SetBackgroundColour(wx.Colour(50, 50, 50))
        self.log.SetForegroundColour("white")

        # self.commands.SetBackgroundColour("black")
        # self.commands.SetForegroundColour("white")
        self.commands.SetHint(_(u"Type commands here"))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.log, wx.EXPAND, wx.EXPAND, 0)
        sizer.Add(self.commands, 0, wx.EXPAND, 0)

        self.SetSizer(sizer)

        self.commands.Bind(wx.EVT_TEXT_ENTER, self.on_command_entered)

    def on_command_entered(self, event):
        """Handle the event when the user enters text."""
        self.cursor = 0
        self.line = self.commands.GetValue()
        self.commands.Clear()  # clear the text box

        command = self.read_command()  # read the first character

        if command == "h":
            self.help_command()
        elif command == "s":
            self.switch_command()
        # elif command == "m":
        #     self.monitor_command()
        # elif command == "z":
        #     self.zap_command()
        elif command == "r":
            self.run_command()
        elif command == "c":
            self.continue_command()
        else:
            if command:
                print(_(u"Error! Invalid command!"))

    def help_command(self):
        """Print a list of valid commands."""
        print(_(u"User commands:"))
        print("r N       - " + _(u"run the simulation for N cycles"))
        print("            " + _(u"(from scratch)"))
        print("c N       - " + _(u"continue the simulation for N"))
        print("            " + _(u"cycles"))
        print("s X N     - " + _(u"set switch X to N (0 or 1)"))
        print("h         - " + _(u"help (this command)"))

    def switch_command(self):
        """Set the specified switch to the specified signal level."""
        switch_id = self.read_name()
        if switch_id is not None:
            switch_state = self.read_number(0, 1)
            if switch_state is not None:
                if self.devices.set_switch(switch_id, switch_state):
                    print(_(u"Successfully set switch."))
                    self.inputsPanel.refresh_list()
                else:
                    print(_(u"Error! Invalid switch."))

    def run_network(self, cycles):
        """Run the network for the specified number of simulation cycles.

        Return True if successful.
        """
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                self.parent.GetParent().statusbar\
                    .SetStatusText(_(u"Error! Network oscillating."))
                print(_(u"Error! Network oscillating."))
                return False
        # self.monitors.display_signals()
        return True

    def run_command(self, gui=False, gui_cycles=None):
        """Run the simulation from scratch."""
        self.global_vars.cycles_completed = 0
        if gui:
            cycles = gui_cycles
        else:
            cycles = self.read_number(0, None)

        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()
            print("".join([_(u"Running for "), str(cycles), _(u" cycle(s)")]))
            self.devices.cold_startup()
            if self.run_network(cycles):
                self.global_vars.cycles_completed += cycles
            self.set_gui_state(True)
            self.canvas.render_signals()

    def continue_command(self, gui=False, gui_cycles=None):
        """Continue a previously run simulation."""
        if gui:
            cycles = gui_cycles
        else:
            cycles = self.read_number(0, None)

        if cycles is not None:  # if the number of cycles provided is valid
            if self.global_vars.cycles_completed == 0:
                print(_(u"Error! Nothing to continue. Run first."))
            elif self.run_network(cycles):
                self.global_vars.cycles_completed += cycles
                print(" ".join([_(u"Continuing for"), str(cycles), _(u"cycles."),
                                _(u"Total:"),
                                str(self.global_vars.cycles_completed)]))
                self.canvas.render_signals()
                self.set_gui_state(True)

    def read_command(self):
        """Return the first non-whitespace character."""
        self.skip_spaces()
        return self.character

    def get_character(self):
        """Move the cursor forward by one character in the user entry."""
        if self.cursor < len(self.line):
            self.character = self.line[self.cursor]
            self.cursor += 1
        else:  # end of the line
            self.character = ""

    def skip_spaces(self):
        """Skip whitespace until a non-whitespace character is reached."""
        self.get_character()
        while self.character.isspace():
            self.get_character()

    def read_string(self):
        """Return the next alphanumeric string."""
        self.skip_spaces()
        name_string = ""
        if not self.character.isalpha():  # the string must start with a letter
            print(_(u"Error! Expected a name."))
            return None
        while self.character.isalnum():
            name_string = "".join([name_string, self.character])
            self.get_character()
        return name_string

    def read_name(self):
        """Return the name ID of the current string if valid.

        Return None if the current string is not a valid name string.
        """
        name_string = self.read_string()
        if name_string is None:
            return None
        else:
            name_id = self.names.query(name_string)
        if name_id is None:
            print(_(u"Error! Unknown name."))
        return name_id

    def read_signal_name(self):
        """Return the device and port IDs of the current signal name.

        Return None if either is invalid.
        """
        device_id = self.read_name()
        if device_id is None:
            return None
        elif self.character == ".":
            port_id = self.read_name()
            if port_id is None:
                return None
        else:
            port_id = None
        return [device_id, port_id]

    def read_number(self, lower_bound, upper_bound):
        """Return the current number.

        Return None if no number is provided or if it falls outside the valid
        range.
        """
        self.skip_spaces()
        number_string = ""
        if not self.character.isdigit():
            print(_(u"Error! Expected a number."))
            return None
        while self.character.isdigit():
            number_string = "".join([number_string, self.character])
            self.get_character()
        number = int(number_string)

        if upper_bound is not None:
            if number > upper_bound:
                print(_(u"Number out of range."))
                return None

        if lower_bound is not None:
            if number < lower_bound:
                print(_(u"Number out of range."))
                return None

        return number
