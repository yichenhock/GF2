"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
Gui - configures the main window and all the widgets.
"""
import sys
import wx
import wx.lib.agw.aui as aui

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
# from dum import DummyParser as Parser

from gui_consoleout_tab import ConsoleOutTab
from gui_circuitdef_tab import CircuitDefTab
from gui_inputs_tab import InputsTab
from gui_monitors_tab import MonitorsTab
from gui_canvas import MyGLCanvas
from global_vars import GlobalVars


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(1024, 768))

        self.SetIcon(wx.Icon('logsim/imgs/favicon.ico'))

        self.path = path
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors

        self.global_vars = GlobalVars()

        if self.path is None:  # open up the file dialog
            if not self.open_file():
                print("Application must be run with a circuit "
                    "definition file.")
                self.Close(True)  # exit the application
                sys.exit()

        self.scanner = Scanner(self.path, names)
        self.parser = Parser(names, devices, network, monitors, self.scanner)

        # Create the menu, toolbar and statusbar
        self.create_menu()
        self.create_tb()
        self.statusbar = self.CreateStatusBar(2)
        self.statusbar.SetStatusWidths([-2, -1])
        self.statusbar.SetStatusText(self.path, 1)

        # create an AuiManager object
        self.mgr = aui.AuiManager()

        # notify AUI which frame to use
        self.mgr.SetManagedWindow(self)

        # # main monitor part
        self.main_panel = wx.Panel(
            self, wx.ID_ANY, size=(wx.EXPAND, wx.EXPAND))
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.canvas_sizer = wx.BoxSizer(wx.VERTICAL)

        self.canvas = MyGLCanvas(
            self.main_panel, devices, monitors, self.global_vars)
        self.y_scroll = wx.ScrollBar(self.main_panel, style=wx.SB_VERTICAL)
        self.x_scroll = wx.ScrollBar(self.main_panel, style=wx.SB_HORIZONTAL)
        self.y_scroll.Disable()
        self.x_scroll.Disable()

        self.main_sizer.Add(self.canvas_sizer, 1,
                            wx.EXPAND | wx.ALL | wx.TOP | wx.LEFT |
                            wx.BOTTOM, 0)
        self.main_sizer.Add(self.y_scroll, 0,
                            wx.EXPAND | wx.TOP | wx.BOTTOM, 0)

        self.canvas_sizer.Add(self.canvas, wx.EXPAND, wx.EXPAND | wx.LEFT, 0)
        self.canvas_sizer.Add(self.x_scroll, 0, wx.EXPAND | wx.ALL, 0)

        self.main_panel.SetSizerAndFit(self.main_sizer)

        self.mgr.AddPane(self.main_panel, aui.AuiPaneInfo().CenterPane())

        # bottom panel
        notebook = aui.AuiNotebook(
            self, wx.ID_ANY, agwStyle=aui.AUI_NB_CLOSE_ON_ALL_TABS)
        self.circuitDefPanel = CircuitDefTab(
            notebook, self.path, self.statusbar, self.global_vars)
        self.inputsPanel = InputsTab(
            notebook, names, devices, self.canvas, self.statusbar)
        self.monitorsPanel = MonitorsTab(
            notebook, names, devices, monitors, self.canvas, self.statusbar)

        self.consoleOutPanel = ConsoleOutTab(notebook, self.path, names,
                                             devices, network,
                                             monitors, self.parser,
                                             self.inputsPanel,
                                             self.set_gui_state,
                                             self.global_vars,
                                             self.canvas, self.save_file)

        with open(self.path, "r") as f:
            self.circuitDefPanel.replace_text(f.read())

        notebook.AddPage(self.consoleOutPanel, "Output", True)
        notebook.AddPage(self.circuitDefPanel, "Circuit Definition", False)
        notebook.AddPage(self.inputsPanel, "Inputs", False)
        notebook.AddPage(self.monitorsPanel, "Monitors", False)

        # disable close buttons
        notebook.SetCloseButton(0, False)
        notebook.SetCloseButton(1, False)
        notebook.SetCloseButton(2, False)
        notebook.SetCloseButton(3, False)

        self.mgr.AddPane(notebook,
                         aui.AuiPaneInfo().CaptionVisible(False).
                         Right().PaneBorder(False).Floatable(False)
                         .GripperTop(False).MinSize(330, 150)
                         .CloseButton(False))

        # setting docking guides fixes docking issue (problem with wxTimer)
        agwFlags = self.mgr.GetAGWFlags()
        self.mgr.SetAGWFlags(agwFlags
                             | aui.AUI_MGR_AERO_DOCKING_GUIDES
                             )

        self.mgr.Update()

        self.y_scroll.Bind(wx.EVT_SCROLL, self.on_y_scroll)
        self.y_scroll.Bind(wx.EVT_SIZE, self.set_scroll)  # when window resizes
        self.x_scroll.Bind(wx.EVT_SCROLL, self.on_x_scroll)
        self.x_scroll.Bind(wx.EVT_SIZE, self.set_scroll)  # when window resizes

        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Centre()
        self.Show(True)

        self.SetSizeHints(minW=600, minH=400)

        self.set_gui_state(sim_running=False)

        print("Logic Simulator: interactive graphical user interface.\n"
              "Enter 'h' for help.")

        # try parsing the network
        self.parse()

    def create_menu(self):
        """Create a menu."""
        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_SAVEAS, "&Save As")
        fileMenu.Append(wx.ID_EXIT, "&Exit")

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")

        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.on_menu)

    def create_tb(self):
        """Create a toolbar."""
        tb = wx.ToolBar(self, - 1, style=wx.TB_TEXT)
        self.ToolBar = tb

        tb.AddTool(1, 'Browse',
                   wx.Image("./logsim/imgs/browse.png",
                            wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
                   shortHelp="Browse for a file")
        tb.AddTool(2, 'Save',
                   wx.Image("./logsim/imgs/save.png",
                            wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
                   shortHelp="Save the file")
        tb.AddTool(3, 'New',
                   wx.Image("./logsim/imgs/new file.png",
                            wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
                   shortHelp="Create a new file")
        tb.AddStretchableSpace()
        tb.AddTool(4, 'Compile',
                   wx.Image("./logsim/imgs/compile.png",
                            wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
                   shortHelp="Compile the circuit definition")
        tb.AddTool(5, 'Run',
                   wx.Image("./logsim/imgs/run.png",
                            wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
                   shortHelp="Run the simulation")
        tb.AddTool(6, 'Continue',
                   wx.Image("./logsim/imgs/continue.png",
                            wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
                   shortHelp="Continue the simulation")
        tb.AddTool(7, 'Reset',
                   wx.Image("./logsim/imgs/reset.png",
                            wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
                   shortHelp="Reset the simulation")

        self.spin = wx.SpinCtrl(tb, wx.ID_ANY, "10")
        # Configure spin
        self.spin.SetMin(1)
        self.spin.SetMax(1000)
        tb.AddControl(self.spin, 'Cycles')

        tb.AddStretchableSpace()
        tb.AddTool(8, 'Save Plot',
                   wx.Image("./logsim/imgs/save image.png",
                            wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
                   shortHelp="Save signal trace as an image")
        tb.AddTool(9, 'Help',
                   wx.Image("./logsim/imgs/help.png",
                            wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
                   shortHelp="Help")
        tb.AddTool(10, 'Quit',
                   wx.Image("./logsim/imgs/quit.png",
                            wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
                   shortHelp="Quit Logic Simulator")

        tb.Realize()

        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.Bind(wx.EVT_TOOL, self.on_tool_click, id=1)
        self.Bind(wx.EVT_TOOL, self.on_tool_click, id=2)
        self.Bind(wx.EVT_TOOL, self.on_tool_click, id=3)
        self.Bind(wx.EVT_TOOL, self.on_tool_click, id=4)
        self.Bind(wx.EVT_TOOL, self.on_tool_click, id=5)
        self.Bind(wx.EVT_TOOL, self.on_tool_click, id=6)
        self.Bind(wx.EVT_TOOL, self.on_tool_click, id=7)
        self.Bind(wx.EVT_TOOL, self.on_tool_click, id=8)
        self.Bind(wx.EVT_TOOL, self.on_tool_click, id=9)

    def update_statusbar(self, text):
        """Update the text on the statusbar."""
        self.statusbar.SetStatusText(text)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Yi Chen Hock, Michael \
                          Stevens and Cindy Wu\n2022",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)
        if Id == wx.ID_SAVEAS:
            self.save_file_as()

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        self.update_statusbar(
            "Number of simulation cycles set to: {}".format(spin_value))

    def on_tool_click(self, event):
        """Map toolbar buttons to functions."""
        if event.GetId() == 1:  # browse
            self.open_file()

        elif event.GetId() == 2:  # save
            self.save_file(self.path)

        elif event.GetId() == 3:  # new file
            self.create_file()

        elif event.GetId() == 4:  # compile aka parse file
            self.parse()

        elif event.GetId() == 5:  # run
            self.on_run_button()

        elif event.GetId() == 6:  # continue
            self.on_cont_button()

        elif event.GetId() == 7:  # reset
            self.on_reset_button()

        elif event.GetId() == 8:  # save plot
            self.save_plot()

        elif event.GetId() == 9:  # help
            self.on_help_button()

        elif event.GetId() == 10:  # quit
            # check first if user has any unsaved changes!!
            if self.global_vars.def_edited:
                resp = wx.MessageBox("Changes you made may not be saved.",
                                     "Quit application?", wx.ICON_WARNING |
                                     wx.OK | wx.CANCEL)
                if resp == wx.OK:
                    self.Close(True)
            else:
                self.Close(True)

    def parse(self):
        """Compiles/parses the circuit definition file."""
        # save the file first
        self.save_file(self.path)

        # reinitialise the scanner and parser
        self.scanner = Scanner(self.path, self.names)
        self.parser = Parser(self.names, self.devices,
                             self.network, self.monitors, self.scanner)

        try:
            if self.parser.parse_network():
                # update the inputs panel
                self.inputsPanel.refresh_list()
                # update the monitors panel
                self.monitorsPanel.initialise_monitor_list()
                self.set_gui_state(sim_running=False)

                self.statusbar.SetStatusText(
                    'File saved and compiled successfully.')
                return True
            else:
                # error has occured while parsing
                self.statusbar.SetStatusText('File compiled with errors.')
                return False
        except Exception:
            self.statusbar.SetStatusText("Parser failed to work :(")

    def on_run_button(self):
        """Run the simulation for N cycles from scratch."""
        if not self.monitors.monitors_dictionary:
            self.statusbar.SetStatusText("No monitors.")
            return

        self.consoleOutPanel.run_command(True, self.spin.GetValue())
        self.update_statusbar("Run button pressed.")
        self.set_gui_state(sim_running=True)
        self.canvas.render_signals(flush_pan=True)

    def on_cont_button(self):
        """Continue the simulation for N cycles."""
        self.consoleOutPanel.continue_command(True, self.spin.GetValue())
        self.update_statusbar("Continue button pressed.")
        self.canvas.render_signals(flush_pan=True)
        self.set_gui_state(sim_running=True)

    def on_reset_button(self):
        """Reset the simulation."""
        self.global_vars.cycles_completed = 0

        self.monitors.reset_monitors()
        print("Simulation reset.")
        self.update_statusbar("Reset button pressed.")
        self.set_gui_state(sim_running=False)
        self.canvas.render_signals(flush_pan=True)

    def set_gui_state(self, sim_running):
        """Set the state of GUI widgets depending on simulation state."""
        self.ToolBar.EnableTool(4, not sim_running)  # disable compile button
        self.ToolBar.EnableTool(5, not sim_running)  # disable run button
        self.ToolBar.EnableTool(6, sim_running)  # enable continue button
        self.ToolBar.EnableTool(7, sim_running)  # enable reset button
        # text box only editable when the simulation is not running
        self.circuitDefPanel.set_textbox_state(not sim_running)
        self.monitorsPanel.enable_monitor(not sim_running)

    def on_help_button(self):
        """Display a helpful message box."""
        wx.MessageBox("Press the buttons :D",
                      "Help", wx.ICON_INFORMATION | wx.OK)

    def on_close(self, event):
        """Deinitialise the frame manager on close."""
        self.mgr.UnInit()
        self.Destroy()

    def check_for_changes(self):
        """Check if the user has any unsaved changes."""
        if self.global_vars.def_edited:
            resp = wx.MessageBox("Changes you made may not be saved.",
                                 "Open a new file?", wx.ICON_WARNING |
                                 wx.OK | wx.CANCEL)
            if resp == wx.OK:
                return True
        else:
            return True
        return False

    def open_file(self):
        """Launch a dialog to select and open a file."""
        if self.check_for_changes():
            with wx.FileDialog(self, "Open File",
                               wildcard="Text documents (*.txt)|*.txt",
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as \
                    file_dialog:
                if file_dialog.ShowModal() == wx.ID_CANCEL:
                    return False  # the user changed their mind

                # Proceed loading the file chosen by the user
                pathname = file_dialog.GetPath()
                return self.load_file(pathname)

    def load_file(self, pathname):
        """Load a file into the GUI."""
        try:
            f = open(pathname)
        except OSError:
            wx.MessageBox("Error opening file.",
                          "Error", wx.ICON_ERROR | wx.OK)
            return False
        self.path = pathname
        try:
            self.statusbar.SetStatusText(pathname, 1)
            self.circuitDefPanel.replace_text(f.read())
        except AttributeError:
            pass
        # write to circuit definition panel
        self.global_vars.def_edited = False
        f.close()
        return True

    def create_file(self):
        """Launch a dialog to select and create a new file."""
        if self.check_for_changes():
            with wx.FileDialog(self, "Save File",
                               defaultFile="new_definition_file.txt",
                               wildcard="Text documents (*.txt)|*.txt",
                               style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as \
                    file_dialog:
                if file_dialog.ShowModal() == wx.ID_CANCEL:
                    return  # the user changed their mind

                # Proceed saving the file chosen by the user
                pathname = file_dialog.GetPath()
                # CREATE A NEW FILE HERE AND SET THAT AS THE NEW PATH!
                try:
                    open(pathname, 'w').close()
                except OSError:
                    print('Failed creating the file')
                    wx.MessageBox("Error creating file.",
                                  "Error", wx.ICON_ERROR | wx.OK)
                else:
                    print('File created successfully in {}'.format(pathname))
                    self.load_file(pathname)

    def save_plot(self):
        """Launch a dialog to save the signal trace as an image."""
        with wx.FileDialog(self, "Save File",
                           defaultFile="image.png",
                           wildcard="PNG files (*.png)|*.png",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as \
                file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Proceed saving the file chosen by the user
            pathname = file_dialog.GetPath()
            self.canvas.save(pathname)

    def save_file(self, pathname):
        """Launch a dialog to save the current file."""
        try:
            with open(pathname, "w") as f:
                f.write(self.circuitDefPanel.get_text())

        except OSError:
            wx.MessageBox("Error saving file.",
                          "Error", wx.ICON_ERROR | wx.OK)
            return

        self.statusbar.SetStatusText('File saved.')
        self.global_vars.def_edited = False

    def save_file_as(self):
        """Launch a dialog for to save the current file as a new file."""
        with wx.FileDialog(self, "Save File",
                           defaultFile="new_definition_file.txt",
                           wildcard="Text documents (*.txt)|*.txt",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as \
                file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Proceed saving the file chosen by the user
            pathname = file_dialog.GetPath()

            # save the file to the new path
            self.save_file(pathname)
            self.load_file(pathname)

    def set_scroll(self, event=None):
        """Set the scrollbar position based on the canvas position."""
        self.canvas.update_dimensions()
        y_scroll_width, y_scroll_height = self.y_scroll.GetSize()
        x_scroll_width, x_scroll_height = self.x_scroll.GetSize()
        self.y_scroll.SetSize(wx.Size(y_scroll_width, self.canvas.height))
        self.x_scroll.SetSize(wx.Size(self.canvas.width, x_scroll_height))

        plot_width = int(self.canvas.plot_width)
        plot_height = int(self.canvas.plot_height)

        if plot_height <= self.canvas.height:
            self.y_scroll.Disable()
        else:
            position = plot_height + self.canvas.pan_y - self.canvas.height
            self.y_scroll.SetScrollbar(position, self.canvas.height,
                                       plot_height, 0)
            self.y_scroll.Enable()

        if plot_width <= self.canvas.width:
            self.x_scroll.Disable()
        else:
            x_position = -1 * self.canvas.pan_x
            self.x_scroll.SetScrollbar(x_position, self.canvas.width,
                                       plot_width, 0)
            self.x_scroll.Enable()

        self.Refresh()

    def on_y_scroll(self, event):
        """Pan the canvas when the user scrolls vertically."""
        position = self.y_scroll.GetThumbPosition()
        self.canvas.pan_y = -(
            self.canvas.plot_height - self.canvas.height - position)
        self.canvas.init = False
        self.canvas.render_signals(set_scroll=False)

    def on_x_scroll(self, event):
        """Pan the canvas when the user scrolls horizontally."""
        x_position = self.x_scroll.GetThumbPosition()
        self.canvas.pan_x = -1 * x_position
        self.canvas.init = False
        self.canvas.render_signals(set_scroll=False)
